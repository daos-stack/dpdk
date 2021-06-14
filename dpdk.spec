# Avoid architecture-specific name of build-dir to fix per-arch reproducibility with doxygen
%global _vpath_builddir %{_vendor}-%{_target_os}-build

Name: dpdk
Version: 21.02
Release: 1%{?dist}
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

%define _includedir %{_datadir}
%define _libdir %{_datadir}
%define sdkdir  %{_datadir}/%{name}
%define docdir  %{_docdir}/%{name}
%define incdir %{_includedir}/%{name}/include
%define pmddir %{_libdir}/%{name}/libs/pmds

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
       -Ddisable_drivers=compress/isal \
  --default-library=shared

# docs fails on el7 with "ValueError: invalid version number 'these.'"
#       -Denable_docs=true \
#       -Dmachine=generic \
#       -Ddrivers_install_subdir=dpdk-pmds \
%meson_build

%install
%meson_install

%files
# BSD
%{_bindir}/dpdk-testpmd
%{_bindir}/dpdk-proc-info
%{_libdir}/*.so.*
%{pmddir}/*.so.*

%files devel
#BSD
%{incdir}/
%{sdkdir}
%ghost %{sdkdir}/mk/exec-env/bsdapp
%ghost %{sdkdir}/mk/exec-env/linuxapp
%{_libdir}/*.so
%{pmddir}/*.so
%exclude %{_libdir}/*.a
%{_libdir}/pkgconfig/libdpdk.pc
%{_libdir}/pkgconfig/libdpdk-libs.pc

%changelog
* Thu Jan 21 2021 Timothy Redaelli <tredaelli@redhat.com> - 2:20.11-1
- Update to 20.11
