# Add option to build as static libraries (--without shared)
%bcond_without shared
# Add option to build without examples
%bcond_with examples
# Add option to build without tools
%bcond_without tools

# Avoid architecture-specific name of build-dir to fix per-arch reproducibility with doxygen
%global _vpath_builddir %{_vendor}-%{_target_os}-build

Name: dpdk
Version: 21.05
Release: 4%{?dist}
Epoch: 0
URL: http://dpdk.org
Source: https://fast.dpdk.org/rel/dpdk-%{version}.tar.xz

BuildRequires: meson


Summary: Set of libraries and drivers for fast packet processing

#
# Note that, while this is dual licensed, all code that is included with this
# Pakcage are BSD licensed. The only files that aren't licensed via BSD is the
# kni kernel module which is dual LGPLv2/BSD, and thats not built for fedora.
#
License: BSD and LGPLv2 and GPLv2

Patch0: 0001-build-meson-disable-libraries-we-don-t-need.patch
Patch1: 0002-build-meson-disable-qat_asym-driver.patch
Patch2: 0003-pci-linux-free-the-device-if-no-kernel-driver-config.patch
Patch3: 0004-ARM64-Cross-Compilation-Support.patch
Patch4: 0005-meson-mlx5-Suppress-Wunused-value-diagnostic.patch

#
# The DPDK is designed to optimize througput of network traffic using, among
# other techniques, carefully crafted assembly instructions.  As such it
# needs extensive work to port it to other architectures.
#
ExclusiveArch: x86_64 i686 aarch64 ppc64le

BuildRequires: gcc
BuildRequires: kernel-headers, libpcap-devel, doxygen, /usr/bin/sphinx-build, zlib-devel
%if (0%{?rhel} >= 7)
BuildRequires: numactl-devel
BuildRequires: epel-rpm-macros
%else
%if (0%{?suse_version} >= 1315)
BuildRequires: libnuma-devel
%endif
%endif
BuildRequires: rdma-core-devel
BuildRequires: python3-pyelftools

%description
The Data Plane Development Kit is a set of libraries and drivers for
fast packet processing in the user space.

%package devel
Summary: Data Plane Development Kit development files
Requires: %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release} python3
%if ! %{with shared}
Provides: %{name}-static = %{?epoch:%{epoch}:}%{version}-%{release}
%endif
Requires: rdma-core-devel

%description devel
This package contains the headers and other files needed for developing
applications with the Data Plane Development Kit.

%if %{with tools}
%package tools
Summary: Tools for setting up Data Plane Development Kit environment
Requires: %{name} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires: kmod pciutils findutils iproute python3-pyelftools

%description tools
%{summary}
%endif

%if %{with examples}
%package examples
Summary: Data Plane Development Kit example applications
BuildRequires: libvirt-devel
BuildRequires: make

%description examples
Example applications utilizing the Data Plane Development Kit, such
as L2 and L3 forwarding.
%endif

%if (0%{?suse_version} >= 1315)
%define docdir %{_datadir}/doc/%{name}
%else
%define docdir %{_docdir}/%{name}
%endif
%define sdkdir  %{_datadir}/%{name}
%define incdir %{_includedir}/%{name}
%define pmddir %{_libdir}/%{name}-pmds

%pretrans -p <lua>
-- This is to clean up directories before links created
-- See https://fedoraproject.org/wiki/Packaging:Directory_Replacement

directories = {
    "/usr/share/dpdk/mk/exec-env/bsdapp",
    "/usr/share/dpdk/mk/exec-env/linuxapp"
}
for i,path in ipairs(directories) do
  st = posix.stat(path)
  if st and st.type == "directory" then
    status = os.rename(path, path .. ".rpmmoved")
    if not status then
      suffix = 0
      while not status do
        suffix = suffix + 1
        status = os.rename(path .. ".rpmmoved", path .. ".rpmmoved." .. suffix)
      end
      os.rename(path, path .. ".rpmmoved")
    end
  end
end
%prep
%setup -q -n dpdk-%{version}

%build
CFLAGS="$(echo %{optflags} -fcommon)" \
%meson --includedir=include/dpdk \
       -Ddrivers_install_subdir=dpdk-pmds \
       -Ddisable_drivers=compress/isal,compress/mlx5,net/mlx4,net/mlx5,vdpa/mlx5,common/mlx5,regex/mlx5,raw/ioat \
%if %{with examples}
       -Dexamples=all \
%endif
%if %{with shared}
  --default-library=shared
%else
  --default-library=static
%endif
# docs fails on el7 with "ValueError: invalid version number 'these.'"
#       -Denable_docs=true \
%meson_build

%install
%meson_install

%files
%exclude %{docdir}
%{_bindir}/dpdk-testpmd
%{_bindir}/dpdk-proc-info
%if %{with shared}
%{_libdir}/*.so.*
%{pmddir}/*.so.*
%endif

%files devel
%exclude %{docdir}
%{incdir}/
%{sdkdir}
%ghost %{sdkdir}/mk/exec-env/bsdapp
%ghost %{sdkdir}/mk/exec-env/linuxapp
%if %{with tools}
%exclude %{_bindir}/dpdk-*.py
%endif
%if %{with examples}
%exclude %{sdkdir}/examples/
%endif
%if ! %{with shared}
%{_libdir}/*.a
%exclude %{_libdir}/*.so
%exclude %{pmddir}/*.so
%else
%{_libdir}/*.so
%{pmddir}/*.so
%exclude %{_libdir}/*.a
%endif
%{_libdir}/pkgconfig/libdpdk.pc
%{_libdir}/pkgconfig/libdpdk-libs.pc

%if %{with tools}
%files tools
%exclude %{docdir}
%{_bindir}/dpdk-pdump
%{_bindir}/dpdk-test
%{_bindir}/dpdk-test-*
%{_bindir}/dpdk-*.py
%endif

%if %{with examples}
%files examples
%exclude %{docdir}
%{_bindir}/dpdk_example_*
%doc %{sdkdir}/examples
%endif

%changelog
* Wed Sep 08 2021 Tom Nabarro <tom.nabarro@intel.com> - 0:21.05-4
- Disable ioat driver.

* Tue Aug 03 2021 Tom Nabarro <tom.nabarro@intel.com> - 0:21.05-3
- Add additional patches to align with commit pinned by SPDK v21.07.

* Tue Jul 06 2021 Johann Lombardi <johann.lombardi@intel.com> - 0:21.05-2
- Disable mlx4 and mlx5 drivers

* Mon Jun 21 2021 Tom Nabarro <tom.nabarro@intel.com> - 0:21.05-1
- Update to 21.05 to align with the SPDK 21.07 release
- Use meson and ninja backend for build

* Wed Feb 10 2021 Brian J. Murrell <brian.murrell@intel.com> - 0:19.11.6-1
- Update to address CVEs
- Tighten up the setting of python path in shebang

* Thu Jan 21 2021 Timothy Redaelli <tredaelli@redhat.com> - 2:20.11-1
- Update to 20.11

* Fri Apr 03 2020 Tom Nabarro <tom.nabarro@intel.com> - 0:19.11-1
- Update to 19.11 to align with the SPDK 20.01.1 release

* Fri Mar 13 2020 Brian J. Murrell <brian.murrell@intel.com> - 0:19.02-2
- Disable CONFIG_RTE_LIBRTE_MLX[45]_PMD for DAOS/spdk

* Mon Sep 30 2019 Brian J. Murrell <brian.murrell@intel.com> - 0:19.02-1
- Update to 67b915b09 to align with the SPDK 19.04.1 release

* Thu Jun 27 2019 Timothy Redaelli <tredaelli@redhat.com> - 18.11.2-1
- Updated to DPDK 18.11.2 (#1713704)
