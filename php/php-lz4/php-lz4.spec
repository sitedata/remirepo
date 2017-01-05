# remirepo spec file for php-lz4
#
# Copyright (c) 2016-2017 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%if 0%{?scl:1}
%global sub_prefix %{scl_prefix}
%scl_package        php-lz4
%endif

%global gh_commit   08a5e24ea13a35e820dc222aa13230d313caa6ae
%global gh_short    %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner    kjdev
%global gh_project  php-ext-lz4
#global gh_date     20160608
%global pecl_name   lz4
%global with_zts    0%{!?_without_zts:%{?__ztsphp:1}}
%global ini_name    40-%{pecl_name}.ini

Summary:       LZ4 Extension for PHP
Name:          %{?sub_prefix}php-lz4
Version:       0.3.1
%if 0%{?gh_date:1}
Release:       0.2.%{gh_date}git%{gh_short}%{?dist}%{!?scl:%{!?nophptag:%(%{__php} -r 'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')}}
%else
Release:       1%{?dist}%{!?scl:%{!?nophptag:%(%{__php} -r 'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')}}
%endif
License:       MIT
Group:         Development/Languages
URL:           https://github.com/%{gh_owner}/%{gh_project}
Source0:       https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{gh_project}-%{version}-%{gh_short}.tar.gz

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: %{?scl_prefix}php-devel
BuildRequires: lz4-devel

Requires:      %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:      %{?scl_prefix}php(api) = %{php_core_api}
%{?_sclreq:Requires: %{?scl_prefix}runtime%{?_sclreq}%{?_isa}}

%if "%{?vendor}" == "Remi Collet" && 0%{!?scl:1} && 0%{?rhel}
# Other third party repo stuff
Obsoletes:     php53-%{pecl_name}  <= %{version}
Obsoletes:     php53u-%{pecl_name} <= %{version}
Obsoletes:     php54-%{pecl_name}  <= %{version}
Obsoletes:     php54w-%{pecl_name} <= %{version}
%if "%{php_version}" > "5.5"
Obsoletes:     php55u-%{pecl_name} <= %{version}
Obsoletes:     php55w-%{pecl_name} <= %{version}
%endif
%if "%{php_version}" > "5.6"
Obsoletes:     php56u-%{pecl_name} <= %{version}
Obsoletes:     php56w-%{pecl_name} <= %{version}
%endif
%if "%{php_version}" > "7.0"
Obsoletes:     php70u-%{pecl_name} <= %{version}
Obsoletes:     php70w-%{pecl_name} <= %{version}
%endif
%if "%{php_version}" > "7.1"
Obsoletes:     php71u-%{pecl_name} <= %{version}
Obsoletes:     php71w-%{pecl_name} <= %{version}
%endif
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
This extension allows LZ4, a compression/decompression library.

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection (%{scl} by %{?scl_vendor}%{!?scl_vendor:rh})}.


%prep
%setup -qc
mv %{gh_project}-%{gh_commit} NTS

cd NTS
# Use the system library
rm -r lz4
# Only in LZ4 1.7.3
sed -e 's/LZ4HC_CLEVEL_MAX/12/' -i lz4.c

# Sanity check, really often broken
extver=$(sed -n '/#define LZ4_EXT_VERSION/{s/.* "//;s/".*$//;p}' php_lz4.h)
if test "x${extver}" != "x%{version}%{?gh_date:-dev}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?gh_date:-dev}.
   exit 1
fi
cd ..

%if %{with_zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif

# Drop in the bit of configuration
cat << 'EOF' | tee %{ini_name}
; Enable '%{summary}' extension module
extension = %{pecl_name}.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure \
    --with-php-config=%{_bindir}/php-config \
    --with-lz4-includedir=/usr \
    --with-libdir=%{_lib} \
    --enable-lz4
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure \
    --with-php-config=%{_bindir}/zts-php-config \
    --with-lz4-includedir=/usr \
    --with-libdir=%{_lib} \
    --enable-lz4
make %{?_smp_mflags}
%endif


%install
rm -rf %{buildroot}
# Install the NTS stuff
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
# Install the ZTS stuff
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif



%check
: Ignore test relying on some specific LZ4 version
%if 0%{?fedora} < 24 && 0%{?rhel} < 7
rm ?TS/tests/{001,003,008,011}.phpt
%else
rm ?TS/tests/011.phpt
%endif

cd NTS
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: Upstream test suite  for NTS extension
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php --show-diff || : ignore

%if %{with_zts}
cd ../ZTS
: Minimal load test for ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: Upstream test suite  for ZTS extension
TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php --show-diff
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license NTS/LICENSE
%doc NTS/CREDITS
%doc NTS/README.md

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Thu Jan  5 2017 Remi Collet <remi@fedoraproject.org> - 0.3.1-1
- update to 0.3.1

* Thu Dec  1 2016 Remi Collet <remi@fedoraproject.org> - 0.3.0-2
- rebuild with PHP 7.1.0 GA

* Thu Nov 17 2016 Remi Collet <remi@fedoraproject.org> - 0.3.0-1
- update to 0.3.0

* Wed Sep 14 2016 Remi Collet <remi@fedoraproject.org> - 0.2.7-2
- rebuild for PHP 7.1 new API version

* Thu Sep  8 2016 Remi Collet <remi@fedoraproject.org> - 0.2.7-1
- update to 0.2.7 (no change)
- open https://github.com/kjdev/php-ext-lz4/pull/13

* Wed Sep  7 2016 Remi Collet <remi@fedoraproject.org> - 0.2.5-1
- new package, version 0.2.5
- open https://github.com/kjdev/php-ext-lz4/pull/11
- open https://github.com/kjdev/php-ext-lz4/pull/12

