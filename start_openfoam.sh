default_container_name="of2112_hisa1.4.6_pt1.10.2_ub22.04"
container_name="${1:-$default_container_name}"
docker start $container_name
docker exec -it $container_name /bin/bash
