NAME    := dpdk
SRC_EXT := xz
PATCHES := v20.11...707692e67.patch x86_64-native-linuxapp-gcc-config      \
	   dpdk-snapshot.sh configlib.sh gen_config_group.sh set_config.sh

include packaging/Makefile_packaging.mk
