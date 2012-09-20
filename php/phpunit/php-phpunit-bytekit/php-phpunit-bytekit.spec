%{!?__pear: %{expand: %%global __pear %{_bindir}/pear}}
%global pear_name bytekit
%global channel pear.phpunit.de

Name:           php-phpunit-bytekit
Version:        1.1.3
Release:        1%{?dist}
Summary:        A command-line tool built on the PHP Bytekit extension

Group:          Development/Libraries
License:        BSD
URL:            http://github.com/sebastianbergmann/bytekit-cli
Source0:        http://pear.phpunit.de/get/%{pear_name}-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  php-pear >= 1:1.9.4
BuildRequires:  php-channel(%{channel})

Requires:       php-common >= 5.3.3
Requires:       php-channel(%{channel})
Requires:       php-pear(pear.symfony.com/Finder) >= 2.1.0
Requires:       php-pear(components.ez.no/ConsoleTools) >= 1.6
Requires(post): %{__pear}
Requires(postun): %{__pear}

Provides:       php-pear(%{channel}/%{pear_name}) = %{version}


%description
Bytekit is a PHP extension that provides userspace access to the opcodes
generated by PHP's compiler.

bytekit-cli is a command-line tool that leverages Bytekit to perform common code
analysis tasks.


%prep
%setup -q -c
[ -f package2.xml ] || mv package.xml package2.xml
mv package2.xml %{pear_name}-%{version}/%{name}.xml
cd %{pear_name}-%{version}


%build
cd %{pear_name}-%{version}
# Empty build section, most likely nothing required.


%install
cd %{pear_name}-%{version}
rm -rf %{buildroot} docdir
%{__pear} install --nodeps --packagingroot %{buildroot} %{name}.xml

# Clean up unnecessary files
rm -rf %{buildroot}%{pear_phpdir}/.??*

# Install XML package description
mkdir -p %{buildroot}%{pear_xmldir}
install -pm 644 %{name}.xml %{buildroot}%{pear_xmldir}


%clean
rm -rf %{buildroot}


%post
%{__pear} install --nodeps --soft --force --register-only \
    %{pear_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{__pear} uninstall --nodeps --ignore-errors --register-only \
        pear.phpunit.de/%{pear_name} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%{pear_xmldir}/%{name}.xml
%{pear_phpdir}/Bytekit
%{_bindir}/bytekit


%changelog
* Mon Aug 27 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.1.3-1
- update to 1.1.3
- add requires php-pear(pear.symfony.com/Finder) >= 2.1.0RC1
- add requires php-pear(components.ez.no/ConsoleTools) >= 1.6
- del requires php-pear(pear.phpunit.de/File_Iterator) >= 1.3.0

* Mon Nov 07 2011 Remi Collet <RPMS@FamilleCollet.com> - 1.1.2-2
- upstream 1.1.2, rebuild for remi repository

* Sun Nov 06 2011 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.1.2-2
- Fix search and replace issue

* Sat Nov 05 2011 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.1.2-1
- upstream 1.1.2

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Dec 18 2009 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.1.1-1
- upstream 1.1.1
- /usr/share/pear/Bytekit wasn't owned

* Thu Nov 26 2009 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.0.0-2
- F-(10|11)

* Wed Oct 14 2009 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.0.0-1
- Initial packaging
