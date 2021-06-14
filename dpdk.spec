# Add option to build as static libraries (--without shared)
%bcond_without shared
# Add option to build without examples
%bcond_with examples
# Add option to build without tools
%bcond_without tools

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
%define newlibsdir %{_datadir}/%{name}/lib
%define newpmdsdir %{newlibsdir}/%{name}-pmds
%define newincldir %{_datadir}/%{name}/include

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
       -Ddisable_drivers=compress/isal \
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
#       -Dmachine=generic \
%meson_build

%install
%meson_install

echo
echo "listing buildroot libdir:"
ls -lah "%{buildroot}%{_libdir}"
echo
echo "listing buildroot includedir:"
ls -lah "%{buildroot}%{_includedir}/%{name}"
echo
echo "listing buildroot datadir:"
ls -lah "%{buildroot}%{_datadir}/%{name}"
echo

nld="%{buildroot}%{newlibsdir}"
rpm --eval "moving libdir to new target library directory ${nld}"
mv "%{buildroot}%{_libdir}" "${nld}"

echo
echo "listing new buildroot libdir:"
ls -lah "%{buildroot}%{newlibsdir}"
echo

nid="%{buildroot}%{newincldir}"
rpm --eval "moving includedir to new target include directory ${nid}"
mv "%{buildroot}%{_includedir}/%{name}" "${nid}"

echo
echo "listing new buildroot includedir:"
ls -lah "%{buildroot}%{newincldir}"
echo

%files
%dir %{newlibsdir}
%exclude %{docdir}
%{_bindir}/dpdk-testpmd
%{_bindir}/dpdk-proc-info
%if %{with shared}
%{newlibsdir}/*.so.*
%{newpmdsdir}/*.so.*
%endif

%files devel
%dir %{newlibsdir}
%exclude %{docdir}
%{newincldir}/
%ghost %{sdkdir}/mk/exec-env/bsdapp
%ghost %{sdkdir}/mk/exec-env/linuxapp
%if %{with tools}
%exclude %{_bindir}/dpdk-*.py
%endif
%if %{with examples}
%{sdkdir}/examples/
%else
%exclude %{sdkdir}/examples/
%endif
%if %{with shared}
%{newlibsdir}/*.so
%{newpmdsdir}/*.so
%exclude %{newlibsdir}/*.a
%else
%{newlibsdir}/*.a
%exclude %{newlibsdir}/*.so
%exclude %{newpmdsdir}/*.so
%endif
%{newlibsdir}/pkgconfig/libdpdk.pc
%{newlibsdir}/pkgconfig/libdpdk-libs.pc

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
* Thu Jan 21 2021 Timothy Redaelli <tredaelli@redhat.com> - 2:20.11-1
- Update to 20.11
