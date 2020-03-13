NAME    := dpdk
SRC_EXT := xz
SOURCE   = http://fast.dpdk.org/rel/$(NAME)-$(VERSION).tar.$(SRC_EXT)
PATCHES := v19.02...67b915b09.patch x86_64-native-linuxapp-gcc-config      \
	   dpdk-snapshot.sh configlib.sh gen_config_group.sh set_config.sh

include packaging/Makefile_packaging.mk
