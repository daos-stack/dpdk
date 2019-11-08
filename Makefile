NAME    := dpdk
SRC_EXT := xz
SOURCE   = http://fast.dpdk.org/rel/$(NAME)-$(VERSION).tar.$(SRC_EXT)
PATCHES := v19.02...67b915b09.patch x86_64-native-linuxapp-gcc-config      \
	   dpdk-snapshot.sh configlib.sh gen_config_group.sh set_config.sh

SLES_12_REPOS := https://download.opensuse.org/repositories/devel:/languages:/python:/backports/SLE_12_SP3/

include packaging/Makefile_packaging.mk