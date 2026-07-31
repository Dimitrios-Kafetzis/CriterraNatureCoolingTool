# Container packaging (D-035): one image built from the distributable wheel,
# running as a non-root user. The container is packaging, not architecture —
# reverse proxy, TLS, and multi-user concerns stay with the host (OQ-31, v2).
#
# Build context expects the wheel in backend/dist (tools/build_wheel.sh):
#
#     tools/build_wheel.sh
#     docker build -t nature-cooling .

FROM python:3.12-slim

RUN useradd --create-home --user-group app

COPY backend/dist/*.whl /tmp/wheels/
RUN pip install --no-cache-dir "$(ls /tmp/wheels/*.whl)[serve]" && rm -rf /tmp/wheels

USER app
WORKDIR /home/app

# Projects live under the platformdirs user-data path (D-028); compose.yaml
# mounts a named volume here so they survive container replacement.
VOLUME /home/app/.local/share/criterra-nature-cooling

EXPOSE 8000
CMD ["nature-cooling", "serve", "--host", "0.0.0.0", "--port", "8000"]
