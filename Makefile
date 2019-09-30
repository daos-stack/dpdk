NAME    := dpdk
SRC_EXT := xz
SOURCE   = http://fast.dpdk.org/rel/$(NAME)-$(VERSION).tar.$(SRC_EXT)
PATCHES :=$(NAME)-b354dddee.patch

SLES_12_REPOS := https://download.opensuse.org/repositories/devel:/languages:/python:/backports/SLE_12_SP3/

include packaging/Makefile_packaging.mk