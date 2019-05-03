# Copyright 2014 6WIND S.A.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# - Neither the name of 6WIND S.A. nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

%{bcond_with doc}

Name: dpdk
Version: 18.02
Release: 3%{?dist}
Packager: packaging@6wind.com
URL: http://dpdk.org
Source: http://dpdk.org/browse/dpdk/snapshot/dpdk-%{version}.tar.gz
Patch1: dpdk-b354dddee.patch

Summary: Data Plane Development Kit core
Group: System Environment/Libraries
License: BSD and LGPLv2 and GPLv2

ExclusiveArch: i686 x86_64 aarch64
%ifarch aarch64
%global machine armv8a
%global target arm64-%{machine}-linuxapp-gcc
%global config arm64-%{machine}-linuxapp-gcc
%else
%global machine default
%global target %{_arch}-%{machine}-linuxapp-gcc
%global config %{_arch}-native-linuxapp-gcc
%endif

# Not needed for the DAOS spdk build
#BuildRequires: kernel-devel, kernel-headers, libpcap-devel
#BuildRequires: doxygen, python-sphinx, inkscape
#BuildRequires: texlive-collection-latexextra
%if (0%{?rhel} >= 7)
BuildRequires:  numactl-devel
%else
%if (0%{?suse_version} > 1315)
BuildRequires:  libnuma-devel
%endif
%endif

%description
DPDK core includes kernel modules, core libraries and tools.
testpmd application allows to test fast packet processing environments
on x86 platforms. For instance, it can be used to check that environment
can support fast path applications such as 6WINDGate, pktgen, rumptcpip, etc.
More libraries are available as extensions in other packages.

%package devel
Summary: Data Plane Development Kit for development
Requires: %{name}%{?_isa} = %{version}-%{release}
%description devel
DPDK devel is a set of makefiles, headers and examples
for fast packet processing on x86 platforms.

%if %{with doc}
%package doc
Summary: Data Plane Development Kit API documentation
BuildArch: noarch
%description doc
DPDK doc is divided in two parts: API details in doxygen HTML format
and guides in sphinx HTML/PDF formats.
%endif

%prep
%setup -q
%patch1 -p1

%build
make O=%{target} T=%{config} config
sed -ri 's,(RTE_MACHINE=).*,\1%{machine},' %{target}/.config
sed -ri 's,(RTE_APP_TEST=).*,\1n,'         %{target}/.config
sed -ri 's,(RTE_BUILD_SHARED_LIB=).*,\1y,' %{target}/.config
sed -ri 's,(RTE_NEXT_ABI=).*,\1n,'         %{target}/.config
sed -ri 's,(LIBRTE_VHOST=).*,\1y,'         %{target}/.config
sed -ri 's,(LIBRTE_PMD_PCAP=).*,\1y,'      %{target}/.config
make CONFIG_RTE_EAL_IGB_UIO=n                  \
     CONFIG_RTE_LIBRTE_KVARGS=n                \
     CONFIG_RTE_LIBRTE_ARK_PMD=n               \
     CONFIG_RTE_LIBRTE_BNX2X_PMD=n             \
     CONFIG_RTE_LIBRTE_BNXT_PMD=n              \
     CONFIG_RTE_LIBRTE_CXGBE_PMD=n             \
     CONFIG_RTE_LIBRTE_DPAA_BUS=n              \
     CONFIG_RTE_LIBRTE_FSLMC_BUS=n             \
     CONFIG_RTE_LIBRTE_ENA_PMD=n               \
     CONFIG_RTE_LIBRTE_ENIC_PMD=n              \
     CONFIG_RTE_LIBRTE_EM_PMD=n                \
     CONFIG_RTE_LIBRTE_IGB_PMD=n               \
     CONFIG_RTE_LIBRTE_IXGBE_PMD=n             \
     CONFIG_RTE_LIBRTE_I40E_PMD=n              \
     CONFIG_RTE_LIBRTE_FM10K_PMD=n             \
     CONFIG_RTE_LIBRTE_AVF_PMD=n               \
     CONFIG_RTE_LIBRTE_NFP_PMD=n               \
     CONFIG_RTE_LIBRTE_QEDE_PMD=n              \
     CONFIG_RTE_LIBRTE_SFC_EFX_PMD=n           \
     CONFIG_RTE_LIBRTE_THUNDERX_NICVF_PMD=n    \
     CONFIG_RTE_LIBRTE_LIO_PMD=n               \
     CONFIG_RTE_LIBRTE_OCTEONTX_PMD=n          \
     CONFIG_RTE_LIBRTE_AVP_PMD=n               \
     CONFIG_RTE_LIBRTE_VIRTIO_PMD=n            \
     CONFIG_RTE_VIRTIO_USER=n                  \
     CONFIG_RTE_LIBRTE_VMXNET3_PMD=n           \
     CONFIG_RTE_LIBRTE_PMD_AF_PACKET=n         \
     CONFIG_RTE_LIBRTE_PMD_BOND=n              \
     CONFIG_RTE_LIBRTE_PMD_FAILSAFE=n          \
     CONFIG_RTE_LIBRTE_VDEV_NETVSC_PMD=n       \
     CONFIG_RTE_LIBRTE_PMD_NULL=n              \
     CONFIG_RTE_LIBRTE_PMD_RING=n              \
     CONFIG_RTE_LIBRTE_PMD_TAP=n               \
     CONFIG_RTE_LIBRTE_BBDEV=n                 \
     CONFIG_RTE_LIBRTE_CRYPTODEV=n             \
     CONFIG_RTE_LIBRTE_SECURITY=n              \
     CONFIG_RTE_LIBRTE_EVENTDEV=n              \
     CONFIG_RTE_LIBRTE_PMD_SKELETON_EVENTDEV=n \
     CONFIG_RTE_LIBRTE_PMD_SW_EVENTDEV=n       \
     CONFIG_RTE_LIBRTE_PMD_OCTEONTX_SSOVF=n    \
     CONFIG_RTE_LIBRTE_RAWDEV=n                \
     CONFIG_RTE_DRIVER_MEMPOOL_STACK=n         \
     CONFIG_RTE_LIBRTE_OCTEONTX_MEMPOOL=n      \
     CONFIG_RTE_LIBRTE_TIMER=n                 \
     CONFIG_RTE_LIBRTE_CFGFILE=n               \
     CONFIG_RTE_LIBRTE_CMDLINE=n               \
     CONFIG_RTE_LIBRTE_HASH=n                  \
     CONFIG_RTE_LIBRTE_EFD=n                   \
     CONFIG_RTE_LIBRTE_MEMBER=n                \
     CONFIG_RTE_LIBRTE_JOBSTATS=n              \
     CONFIG_RTE_LIBRTE_METRICS=n               \
     CONFIG_RTE_LIBRTE_BITRATE=n               \
     CONFIG_RTE_LIBRTE_LATENCY_STATS=n         \
     CONFIG_RTE_LIBRTE_LPM=n                   \
     CONFIG_RTE_LIBRTE_ACL=n                   \
     CONFIG_RTE_LIBRTE_POWER=n                 \
     CONFIG_RTE_LIBRTE_IP_FRAG=n               \
     CONFIG_RTE_LIBRTE_GRO=n                   \
     CONFIG_RTE_LIBRTE_GSO=n                   \
     CONFIG_RTE_LIBRTE_METER=n                 \
     CONFIG_RTE_LIBRTE_FLOW_CLASSIFY=n         \
     CONFIG_RTE_LIBRTE_SCHED=n                 \
     CONFIG_RTE_LIBRTE_DISTRIBUTOR=n           \
     CONFIG_RTE_LIBRTE_REORDER=n               \
     CONFIG_RTE_LIBRTE_PORT=n                  \
     CONFIG_RTE_LIBRTE_TABLE=n                 \
     CONFIG_RTE_LIBRTE_PIPELINE=n              \
     CONFIG_RTE_LIBRTE_KNI=n                   \
     CONFIG_RTE_LIBRTE_PMD_KNI=n               \
     CONFIG_RTE_KNI_KMOD=n                     \
     CONFIG_RTE_LIBRTE_PDUMP=n                 \
     CONFIG_RTE_LIBRTE_VHOST=n                 \
     CONFIG_RTE_LIBRTE_PMD_VHOST=n             \
     CONFIG_RTE_APP_TEST=n                     \
     CONFIG_RTE_PROC_INFO=n                    \
     CONFIG_RTE_TEST_PMD=n                     \
     CONFIG_RTE_APP_CRYPTO_PERF=n              \
     CONFIG_RTE_APP_EVENTDEV=n                 \
     CONFIG_RTE_LIBRTE_PMD_PCAP=n              \
     O=%{target} %{?_smp_mflags}
%if %{with doc}
make O=%{target} doc
%endif

%install
rm -rf %{buildroot}
make install O=%{target} DESTDIR=%{buildroot} \
	prefix=%{_prefix} bindir=%{_bindir} sbindir=%{_sbindir} \
	includedir=%{_includedir}/dpdk libdir=%{_libdir} \
	datadir=%{_datadir}/dpdk docdir=%{_docdir}/dpdk

%files
%dir %{_datadir}/dpdk
%{_datadir}/dpdk/usertools
%{_sbindir}/*
%{_bindir}/*
%{_libdir}/*

%files devel
%{_includedir}/dpdk
%{_datadir}/dpdk/mk
%{_datadir}/dpdk/buildtools
%{_datadir}/dpdk/%{target}
%{_datadir}/dpdk/examples

%if %{with doc}
%files doc
%doc %{_docdir}/dpdk
%endif

%post
/sbin/ldconfig
/sbin/depmod

%postun
/sbin/ldconfig
/sbin/depmod

%changelog
* Fri Apr 05 2019 Brian J. Murrell <brian.murrell@intel.com> - 0:18.02-3
- dist macro should be conditionally substituted with ?
- Support SLES 12.3

* Fri Apr 05 2019 Brian J. Murrell <brian.murrell@intel.com> - 0:18.02-2
- Fix patch name to reflect our current spdk is actually at b354dddee
  not 92924b207

* Thu Apr 04 2019 Brian J. Murrell <brian.murrell@intel.com> - 0:18.02-1
- Initial RPM release
- Specialized build for use with spdk
- Added a patch to catch 18.02 up to 92924b207 where our current
  spdk build is
