# remirepo spec file for php-punic, from
#
# Fedora spec file for php-punic
#
# Copyright (c) 2015 Shawn Iwinski <shawn.iwinski@gmail.com>
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#

%global github_owner     punic
%global github_name      punic
%global github_version   1.6.3
%global github_commit    5805b35d6a574f754b49be1f539aaf3ae6484808

%global composer_vendor  punic
%global composer_project punic

# "php": ">=5.3"
%global php_min_ver 5.3

# Build using "--without tests" to disable tests
%global with_tests 0%{!?_without_tests:1}

%{!?phpdir:  %global phpdir  %{_datadir}/php}

Name:          php-%{composer_project}
Version:       %{github_version}
Release:       1%{?github_release}%{?dist}
Summary:       PHP-Unicode CLDR

Group:         Development/Libraries
# Code is MIT, data is Unicode
License:       MIT and Unicode
URL:           http://punic.github.io/

# GitHub export does not include tests.
# Run php-punic-get-source.sh to create full source.
Source0:       %{name}-%{github_version}-%{github_commit}.tar.gz
Source1:       %{name}-get-source.sh

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:     noarch
# Relative paths
BuildRequires: python
# Tests
%if %{with_tests}
BuildRequires: %{_bindir}/phpunit
## composer.json
BuildRequires: php(language) >= %{php_min_ver}
## phpcompatinfo (computed from version 1.6.3)
BuildRequires: php-date
BuildRequires: php-iconv
BuildRequires: php-intl
BuildRequires: php-json
BuildRequires: php-mbstring
BuildRequires: php-pcre
BuildRequires: php-spl
## Autoloader
BuildRequires: php-composer(symfony/class-loader)
%endif

# composer.json
Requires:      php(language) >= %{php_min_ver}
# phpcompatinfo (computed from version 1.6.3)
Requires:      php-date
Requires:      php-iconv
Requires:      php-intl
Requires:      php-json
Requires:      php-mbstring
Requires:      php-pcre
# Autoloader
Requires:      php-composer(symfony/class-loader)
Requires:      php-spl

# Standard "php-{COMPOSER_VENDOR}-{COMPOSER_PROJECT}" naming
Provides:      php-%{composer_vendor}-%{composer_project} = %{version}-%{release}
# Composer
Provides:      php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
PHP-Unicode CLDR Toolkit

Punic is a PHP library using the CLDR data to help you localize various
variables like numbers, dates, units, lists, ...

For full API reference see the APIs reference [1].

[1] http://punic.github.io/docs


%prep
%setup -qn %{github_name}-%{github_commit}

: Create autoloader
cat <<'AUTOLOAD' | tee code/autoload.php
<?php
/**
 * Autoloader for %{name} and its' dependencies
 *
 * Created by %{name}-%{version}-%{release}
 *
 * @return \Symfony\Component\ClassLoader\ClassLoader
 */

if (!isset($fedoraClassLoader) || !($fedoraClassLoader instanceof \Symfony\Component\ClassLoader\ClassLoader)) {
    if (!class_exists('Symfony\\Component\\ClassLoader\\ClassLoader', false)) {
        require_once '%{phpdir}/Symfony/Component/ClassLoader/ClassLoader.php';
    }

    $fedoraClassLoader = new \Symfony\Component\ClassLoader\ClassLoader();
    $fedoraClassLoader->register();
}

$fedoraClassLoader->addPrefix('Punic\\', dirname(__DIR__));

return $fedoraClassLoader;
AUTOLOAD


%build
# Empty build section, nothing to build


%install
rm -rf     %{buildroot}

: Library
mkdir -p %{buildroot}%{phpdir}/Punic
cp -rp code/* %{buildroot}%{phpdir}/Punic/

: Data
mkdir -p %{buildroot}%{_datadir}
mv %{buildroot}%{phpdir}/Punic/data %{buildroot}%{_datadir}/%{name}
ln -s \
    ../../%{name} \
    %{buildroot}%{phpdir}/Punic/data


%check
%if %{with_tests}
%{_bindir}/phpunit \
  -d memory_limit=-1 \
  --bootstrap %{buildroot}%{phpdir}/Punic/autoload.php \
  --verbose
%else
: Tests skipped
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE.txt
%license UNICODE-LICENSE.txt
%doc *.md
%doc composer.json
%{phpdir}/Punic
%{_datadir}/%{name}


%changelog
* Mon Sep 21 2015 Remi Collet <remi@remirepo.net> - 1.6.3-1
- backport for #remirepo

* Fri Sep 11 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.6.3-1
- Initial package
