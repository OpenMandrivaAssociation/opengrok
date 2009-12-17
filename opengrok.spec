Summary:	Source browser and indexer
Name:		opengrok
Version:	0.8.1
Release:	%mkrel 1
Group:		Development/Java
License:	CDDL
URL:		http://www.opensolaris.org/os/project/opengrok/
Source0:        http://hub.opensolaris.org/bin/download/Project+opengrok/files/opengrok-%{version}-src.tar.gz
# hg clone -r786 ssh://anon@hg.opensolaris.org/hg/opengrok/trunk opengrok-0.8-src
# tar czf opengrok-r786-src.tar.gz --exclude .hg opengrok-0.8-src
#Source0:	opengrok-r786-src.tar.gz
Source1:	opengrok
Source2:	configuration.xml
Source3:	opengrok-README.Fedora.webapp
Source4:	opengrok-README.Fedora.nowebapp
Patch0:		opengrok-0.5-jrcs-import.patch
Patch1:		opengrok-0.7-nocplib.patch
Patch3:		opengrok-0.8-manifest-classpath.patch
Patch4:		opengrok-0.6-nooverview.patch
Patch5:		opengrok-0.6-nochangeset.patch
Patch6:		opengrok-0.7-jflex.patch
Requires:	ant
Requires:	bcel
Requires:	ctags
Requires:	jakarta-oro
Requires:	java
Requires:	javacc
Requires:	java-cup
Requires:	jpackage-utils
Requires:	lucene > 2
Requires:	lucene-contrib > 2
Requires:	servlet
Requires:	swing-layout
BuildRequires:	ant
BuildRequires:	ant-junit
BuildRequires:	ant-nodeps
BuildRequires:	bcel
BuildRequires:	ctags
BuildRequires:	docbook2x
BuildRequires:	jakarta-oro
BuildRequires:	javacc
BuildRequires:	java-cup
BuildRequires:	java-devel >= 1.6
BuildRequires:	java-rpmbuild
BuildRequires:	jflex >= 1.4
BuildRequires:	jpackage-utils
BuildRequires:	junit4
BuildRequires:	lucene > 2
BuildRequires:	lucene-contrib > 2
BuildRequires:	servlet
BuildRequires:	swing-layout
BuildRequires:	unzip
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
OpenGrok is a fast and usable source code search and cross reference engine,
written in Java. It helps you search, cross-reference and navigate your source
tree. It can understand various program file formats and version control
histories like SCCS, RCS, CVS, Subversion and Mercurial.

%package	javadoc
Summary:	Javadoc for %{name}
Group:		Books/Other
Requires:	jpackage-utils

%description	javadoc
%{summary}.


%package	tomcat5
Summary:	Source browser web application
Group:		System/Servers
Requires:	%{name} tomcat5

%description	tomcat5
OpenGrok web application


%prep

%setup -q -n %{name}-%{version}-src
%{__unzip} -q ext/jrcs.zip
%patch0 -p1 -b .jrcs-import
%patch1 -p1 -b .nocplib
%patch3 -p0 -b .manifest-classpath
%patch4 -p1 -b .nooverview
%patch5 -p1 -b .nochangeset
%patch6 -p1 -b .jflex

# This is not strictly needed, but to nuke prebuilt stuff
# makes us feel warmer while building
find -name '*.jar' -o -name '*.class' -o -name '*.war' -exec rm -f '{}' \;

# jrcs' javacc directory
sed '
        s,\(property name="javacc.lib.dir" value="\)[^"]*,\1%{_javadir},;
        s,\(javacchome="\)[^"]*,\1${javacc.lib.dir},;
' -i jrcs/build.xml

# Default war configuration
sed 's,/opengrok/configuration.xml,%{_sysconfdir}/%{name}/configuration.xml,' \
        -i conf/web.xml

# README.webapp
cp %{SOURCE3} README.webapp

%build
pushd jrcs
CLASSPATH=$(build-classpath oro) %{ant} -v all

popd
CLASSPATH=$(build-classpath jflex java_cup) %{ant} -v jar javadoc                                           \
        -Dfile.reference.org.apache.commons.jrcs.diff.jar=jrcs/lib/org.apache.commons.jrcs.diff.jar \
        -Dfile.reference.org.apache.commons.jrcs.rcs.jar=jrcs/lib/org.apache.commons.jrcs.rcs.jar \
        -Dfile.reference.lucene-core-2.2.0.jar=$(build-classpath lucene)                        \
        -Dfile.reference.lucene-spellchecker-2.2.0.jar=$(build-classpath lucene-contrib/lucene-spellchecker) \
        -Dfile.reference.ant.jar=$(build-classpath ant)                                         \
        -Dfile.reference.bcel-5.1.jar=$(build-classpath bcel)                                   \
        -Dfile.reference.jakarta-oro-2.0.8.jar=$(build-classpath jakarta-oro)                   \
        -Dfile.reference.servlet-api.jar=$(build-classpath servlet)                             \
        -Dfile.reference.swing-layout-0.9.jar=$(build-classpath swing-layout)

# SolBook is more-or-less DocBook subset, so this can be done safely
# FIXME: db2x_docbook2man output is not as nice as it should be
sed '
        s,^<!DOCTYPE.*,<!DOCTYPE refentry PUBLIC "-//OASIS//DTD DocBook XML V4.2//EN" "docbookx.dtd">,
        s,^<?Pub Inc>,,
' dist/opengrok.1 |docbook2man -


%check
pushd jrcs
CLASSPATH=$(build-classpath junit4) %{ant} test

popd
#CLASSPATH=$(build-classpath jflex junit4) %{ant} test

%install
rm -rf %{buildroot}

# directories

%define webappdir %{_localstatedir}/lib/tomcat5/webapps/source
install -d %{buildroot}%{webappdir}
install -d %{buildroot}%{webappdir}/WEB-INF/lib

install -d %{buildroot}%{_javadir}
install -d %{buildroot}%{_javadocdir}/%{name}
install -d %{buildroot}%{_javadocdir}/%{name}-jrcs
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_localstatedir}/lib/%{name}/data
install -d %{buildroot}%{_localstatedir}/lib/%{name}/src
install -d %{buildroot}%{_datadir}/pixmaps

# jar
install -p -m 644 dist/opengrok.jar %{buildroot}%{_javadir}/opengrok-%{version}.jar
ln -sf opengrok-%{version}.jar %{buildroot}%{_javadir}/opengrok.jar

# jrcs
install -d %{buildroot}%{_javadir}/opengrok-jrcs

install -p -m 644 jrcs/lib/org.apache.commons.jrcs.rcs.jar \
        %{buildroot}%{_javadir}/opengrok-jrcs/org.apache.commons.jrcs.rcs-%{version}.jar
ln -sf org.apache.commons.jrcs.rcs-%{version}.jar \
        %{buildroot}%{_javadir}/opengrok-jrcs/org.apache.commons.jrcs.rcs.jar

install -p -m 644 jrcs/lib/org.apache.commons.jrcs.diff.jar \
        %{buildroot}%{_javadir}/opengrok-jrcs/org.apache.commons.jrcs.diff-%{version}.jar
ln -sf org.apache.commons.jrcs.diff-%{version}.jar \
        %{buildroot}%{_javadir}/opengrok-jrcs/org.apache.commons.jrcs.diff.jar

# bin
install -p -m 755 %{SOURCE1} %{buildroot}%{_bindir}

# man
install -p -m 644 opengrok.1 %{buildroot}%{_mandir}/man1


# javadoc
cp -pR dist/javadoc/. %{buildroot}%{_javadocdir}/%{name}
cp -pR jrcs/doc/api/. %{buildroot}%{_javadocdir}/%{name}-jrcs

# Configuration file configuration.xml
install -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}

# Make love, not war!
unzip -q dist/source.war -d %{buildroot}%{webappdir}
(IFS=:; for file in $(build-classpath                   \
        bcel jakarta-oro swing-layout                   \
        lucene lucene-contrib/lucene-spellchecker)      \
        %{_javadir}/opengrok.jar                        \
        %{_javadir}/opengrok-jrcs/org.apache.commons.jrcs.diff.jar \
        %{_javadir}/opengrok-jrcs/org.apache.commons.jrcs.rcs.jar
do
        ln -sf $file %{buildroot}%{webappdir}/WEB-INF/lib
done)

sed -i 's/\/etc\/etc\//\/etc\//' %{buildroot}%{webappdir}/WEB-INF/web.xml

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc CHANGES.txt LICENSE.txt README.txt doc/EXAMPLE.txt README.webapp
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/configuration.xml
%{_javadir}/*
%{_bindir}/opengrok
%{_mandir}/man1/opengrok.1*
%{_localstatedir}/lib/%{name}

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/*

%files tomcat5
%defattr(-,root,root,-)
%{webappdir}
%config(noreplace) %{webappdir}/WEB-INF/web.xml
%config(noreplace) %{webappdir}/index_body.html
