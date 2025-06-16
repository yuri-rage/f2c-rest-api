# *** BUILD STAGE ***

FROM ubuntu:noble AS build

WORKDIR /app
ENV VIRTUAL_ENV=/app/venv

RUN apt update && apt install -y --no-install-recommends \
    build-essential ca-certificates cmake \
    doxygen g++ git libeigen3-dev libgdal-dev libpython3-dev \
    python3 python3-venv lcov libgtest-dev libtbb-dev swig \
    libgeos-dev libtinyxml2-dev nlohmann-json3-dev

RUN git clone  https://github.com/yuri-rage/f2c-rest-api.git .

RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -U pip
RUN pip install -r requirements.txt

WORKDIR /Fields2Cover
RUN git clone https://github.com/Fields2Cover/Fields2Cover.git .

WORKDIR /Fields2Cover/build
RUN . "$VIRTUAL_ENV/bin/activate" && cmake -DBUILD_PYTHON=ON ..
RUN . "$VIRTUAL_ENV/bin/activate" && make -j$(nproc)

# copy swig bindings to venv
RUN cp /Fields2Cover/build/swig/python/_fields2cover_python.so /app/venv/lib/python3.12/site-packages/_fields2cover_python.so 
RUN cp /Fields2Cover/build/swig/python/fields2cover.py /app/venv/lib/python3.12/site-packages/fields2cover.py 

# *** RUNTIME STAGE ***

FROM ubuntu:noble AS runtime
WORKDIR /app

# use same venv as build
COPY --from=build /app .
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# copy runtime dependencies from build directory
COPY --from=build /Fields2Cover/build/libFields2Cover.so /usr/local/lib
COPY --from=build /Fields2Cover/build/_deps/ortools-src/lib/libortools.so* /usr/local/lib
COPY --from=build /Fields2Cover/build/_deps/steering_functions-build/libsteering_functions.so* /usr/local/lib
COPY --from=build /Fields2Cover/build/_deps/matplot-build/source/matplot/libmatplot.so* /usr/local/lib

RUN apt update && apt install -y --no-install-recommends python3 libpython3.12 \
    libgdal34 libtinyxml2-dev && \
    apt clean && rm -rf /var/lib/apt/lists/*
 
CMD ["./run.py"]

