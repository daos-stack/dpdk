NAME    := dpdk
SRC_EXT := gz
SOURCE   = http://dpdk.org/browse/dpdk/snapshot/dpdk-$(VERSION).tar.$(SRC_EXT)
PATCHES :=$(NAME)-b354dddee.patch

include Makefile_packaging.mk

