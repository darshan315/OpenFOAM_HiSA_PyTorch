default_container_name="of2106_hisa1.4.6_pt1.9.0_ub1804"
container_name="${1:-$default_container_name}"
docker start $container_name
docker exec -it $container_name /bin/bash
