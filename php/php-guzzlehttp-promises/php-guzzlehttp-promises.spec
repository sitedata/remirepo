# remirepo spec file for php-guzzlehttp-promises, from
#
# Fedora spec file for php-guzzlehttp-promises
#
# Copyright (c) 2015-2016 Shawn Iwinski <shawn.iwinski@gmail.com>
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#

%global github_owner     guzzle
%global github_name      promises
%global github_version   1.3.0
%global github_commit    2693c101803ca78b27972d84081d027fca790a1e

%global composer_vendor  guzzlehttp
%global composer_project promises

# "php": ">=5.5.0"
%global php_min_ver 5.5.0

# Build using "--without tests" to disable tests
%global with_tests 0%{!?_without_tests:1}

%{!?phpdir:  %global phpdir  %{_datadir}/php}

Name:          php-%{composer_vendor}-%{composer_project}
Version:       %{github_version}
Release:       1%{?github_release}%{?dist}
Summary:       Guzzle promises library

Group:         Development/Libraries
License:       MIT
URL:           https://github.com/%{github_owner}/%{github_name}
Source0:       %{url}/archive/%{github_commit}/%{name}-%{github_version}-%{github_commit}.tar.gz

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:     noarch
# Tests
%if %{with_tests}
## composer.json
BuildRequires: php(language) >= %{php_min_ver}
BuildRequires: php-composer(phpunit/phpunit)
## phpcompatinfo (computed from version 1.3.0)
BuildRequires: php-json
BuildRequires: php-reflection
BuildRequires: php-spl
## Autoloader
BuildRequires: php-composer(fedora/autoloader)
%endif

# composer.json
Requires:      php(language) >= %{php_min_ver}
# phpcompatinfo (computed from version 1.3.0)
Requires:      php-json
Requires:      php-spl
# Autoloader
Requires:      php-composer(fedora/autoloader)

# Composer
Provides:      php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
Promises/A+ [1] implementation that handles promise chaining and resolution
interactively, allowing for "infinite" promise chaining while keeping the
stack size constant.

Autoloader: %{phpdir}/GuzzleHttp/Promise/autoload.php

[1] https://promisesaplus.com/


%prep
%setup -qn %{github_name}-%{github_commit}

: Create autoloader
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
/**
 * Autoloader for %{name} and its' dependencies
 * (created by %{name}-%{version}-%{release}).
 */
require_once '%{phpdir}/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('GuzzleHttp\\Promise\\', __DIR__);

require_once __DIR__ . '/functions_include.php';
AUTOLOAD


%build
# Empty build section, nothing required


%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{phpdir}/GuzzleHttp/Promise
cp -rp src/* %{buildroot}%{phpdir}/GuzzleHttp/Promise/


%check
%if %{with_tests}
sed "s#require.*autoload.*#require '%{buildroot}%{phpdir}/GuzzleHttp/Promise/autoload.php';#" \
    -i tests/bootstrap.php

# remirepo:11
run=0
ret=0
if which php56; then
   php56 %{_bindir}/phpunit || ret=1
   run=1
fi
if which php71; then
   php71 %{_bindir}/phpunit || ret=1
   run=1
fi
if [ $run -eq 0 ]; then
%{_bindir}/phpunit --verbose
# remirepo:2
fi
exit $ret
%else
: Tests skipped
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc *.md
%doc composer.json
%dir %{phpdir}/GuzzleHttp
     %{phpdir}/GuzzleHttp/Promise


%changelog
* Wed Dec 07 2016 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.3.0-1
- Updated to 1.3.0 (RHBZ #1396687)
- Change autoloader from php-composer(symfony/class-loader) to
  php-composer(fedora/autoloader)

* Sun May 29 2016 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.2.0-1
- Updated to 1.2.0 (RHBZ #1337366)

* Sun Mar 13 2016 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.1.0-1
- Updated to 1.1.0 (RHBZ #1315685)

* Mon Oct 26 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.0.3-1
- Updated to 1.0.3 (RHBZ #1272280)

* Sun Aug 16 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.0.2-1
- Updated to 1.0.2 (RHBZ #1253996)

* Mon Jul 20 2015 Remi Collet <remi@remirepo.net> - 1.0.1-3
- add EL-5 stuff, backport for #remirepo

* Sun Jul 19 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.0.1-3
- Use full paths in autoloader

* Wed Jul 08 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.0.1-2
- Add autoloader dependencies
- Modify autoloader

* Mon Jul 06 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.0.1-1
- Initial package
