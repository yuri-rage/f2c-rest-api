import fields2cover as f2c
from fastapi import FastAPI, Body, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any
from app.models import SwathGeneratorType, RouteGeneratorType
import math
import json

app = FastAPI(
    title="Fields2Cover REST API",
    version="0.1.0-alpha",
    description="A REST API for field coverage path planning using Fields2Cover",
)


@app.post("/plan-path")
async def process_field(request: Request, data: Dict[str, Any] = Body(...)):
    clientHost = request.client.host if request.client else "unknown"
    print(f"Request from {clientHost}")

    robot = f2c.Robot()
    cell = f2c.Cell()

    robotData = data.get("robot", {})
    if not robotData:
        return {"status": "error", "message": "Robot (vehicle) data is required"}

    robot.setWidth(robotData.get("width", 1.0))
    robot.setCovWidth(robotData.get("cov-width", 1.0))
    minTurningRadius = robotData.get("min-turning-radius", 0.0)
    robot.setMinTurningRadius(minTurningRadius)
    robot.setMaxDiffCurv(minTurningRadius / 10.0)

    geometryData = data.get("geometry", {})
    if (
        not isinstance(geometryData, dict)
        or geometryData.get("type") != "MultiPolygon"
        or not geometryData.get("coordinates")
    ):
        return {
            "status": "error",
            "message": ("Invalid geometry: must be a MultiPolygon with coordinates"),
        }

    try:
        for polygon in geometryData["coordinates"]:
            for ring in polygon:
                ring_points = [f2c.Point(p[0], p[1]) for p in ring]
                cell.addRing(f2c.LinearRing(f2c.VectorPoint(ring_points)))
    except (IndexError, TypeError, KeyError) as e:
        return {"status": "error", "message": f"Invalid coordinate data: {str(e)}"}

    headlandDist = data.get("headland-dist", 0.0)
    cells = f2c.Cells()
    cells.addGeometry(cell)
    headlandGenerator = f2c.HG_Const_gen()
    cellsNoHeadlands = headlandGenerator.generateHeadlands(cells, headlandDist)
    swathGenerator = f2c.SG_BruteForce()

    swathType = SwathGeneratorType(
        data.get("swath", {}).get("type", SwathGeneratorType.SWATH_LENGTH)
    )
    routeType = RouteGeneratorType(
        data.get("route", {}).get("type", RouteGeneratorType.BOUSTROPHEDON)
    )

    cellsToProcess = (
        cellsNoHeadlands
        if routeType == RouteGeneratorType.ADVANCED
        else cellsNoHeadlands.getGeometry(0)
    )

    decomposeAngle = data.get("decompose-angle", -1.0)
    if routeType == RouteGeneratorType.ADVANCED and decomposeAngle >= 0.0:
        decomp = f2c.DECOMP_TrapezoidalDecomp()
        decomp.setSplitAngle(decomposeAngle * math.pi / 180.0)
        cellsToProcess = decomp.decompose(cellsToProcess)

    if swathType == SwathGeneratorType.ANGLE:
        angle = data["swath"].get("angle", 0) * math.pi / 180.0
        swaths = swathGenerator.generateSwaths(
            angle, robot.getCovWidth(), cellsToProcess
        )
    elif swathType == SwathGeneratorType.N_SWATH:
        n_swath_obj = f2c.OBJ_NSwath()
        swaths = swathGenerator.generateBestSwaths(
            n_swath_obj, robot.getCovWidth(), cellsToProcess
        )
    else:  # SwathGeneratorType.SWATH_LENGTH
        l_swath_obj = f2c.OBJ_SwathLength()
        swaths = swathGenerator.generateBestSwaths(
            l_swath_obj, robot.getCovWidth(), cellsToProcess
        )

    swathSorter = None
    if routeType == RouteGeneratorType.BOUSTROPHEDON:
        print("Using boustrophedon route planner.")
        swathSorter = f2c.RP_Boustrophedon()
    elif routeType == RouteGeneratorType.SNAKE:
        print("Using snake route planner.")
        swathSorter = f2c.RP_Snake()
    elif routeType == RouteGeneratorType.SPIRAL:
        print("Using spiral route planner")
        numSpirals = data.get("route", {}).get("spirals", 2)
        swathSorter = f2c.RP_Spiral(numSpirals)

    startpoint = data.get("route", {}).get("startpoint", 1)

    if swathSorter:
        swaths = swathSorter.genSortedSwaths(swaths, startpoint)
    else:  # use advanced route planner as the fallback/default
        print("Using advanced route planner.")
        rp = f2c.RP_RoutePlannerBase()
        swaths = rp.genRoute(cellsToProcess, swaths)
        if startpoint % 2 == 0:
            swaths = reverseRoute(swaths)

    dubins = f2c.PP_DubinsCurves()
    pathPlanner = f2c.PP_PathPlanning()
    path = pathPlanner.planPath(robot, swaths, dubins)

    minWPDistance = data.get("min-wp-distance", 1.0)
    path.reduce(minWPDistance)
    path = reduceSameSegmentPoints(path)

    pathLine = path.toLineString()

    # gnuplot dependency adds a lot of X11 bloat to a docker image
    # uncomment this if debug visualization is desired
    # f2c.Visualizer.figure()
    # f2c.Visualizer.plot(cells.getGeometry(0))
    # f2c.Visualizer.plot(cellsToProcess)
    # f2c.Visualizer.plot(path)
    # f2c.Visualizer.save("output.png")

    print(f"Planned {path.size()} waypoints.")

    return {
        "status": "success",
        "length": path.length(),
        "path": json.loads(pathLine.exportToJson()),
    }


def reverseRoute(route):
    reversed_route = f2c.Route()
    for i in range(route.sizeVectorSwaths() - 1, -1, -1):
        reversed_route.addConnection(route.getConnection(i + 1))
        swaths_to_add = route.getSwaths(i).clone()
        swaths_to_add.reverse()
        reversed_route.addSwaths(swaths_to_add)
    if route.sizeConnections() > 0:
        reversed_route.addConnection(route.getConnection(0))
    return reversed_route


def reduceSameSegmentPoints(path):
    if path.size() <= 2:
        return path
    result = f2c.Path()
    result.addState(path.getState(0))
    for i in range(1, path.size() - 1):
        prev = path.getState(i - 1)
        cur = path.getState(i)
        if cur.angle != prev.angle:
            # Keep the point before the angle change
            result.addState(prev)
            # Keep the point where angle changes
            result.addState(cur)
    result.addState(path.getState(path.size() - 1))
    return result


@app.get("/")
async def root():
    """
    JSON response with name, version, and endpoints
    """
    return {
        "name": app.title,
        "version": app.version,
        "status": "success",
        "endpoints": {"root": "/", "plan_path": "/plan-path"},
    }


@app.get("/favicon.ico")
async def favicon():
    """
    simply redirect to the Fields2Cover favicon
    """
    return RedirectResponse(url="https://fields2cover.github.io/_static/favicon.ico")
