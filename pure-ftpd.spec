Summary:	Lightweight, fast and secure FTP server
Name:		pure-ftpd
Version:	1.0.36
Release:	1
License:	GPL
Group:		System/Servers
URL:		http://www.pureftpd.org
Source0:	http://download.pureftpd.org/pub/pure-ftpd/releases/%{name}-%{version}.tar.gz
Source1:	pure-ftpd.init
Source2:	pure-ftpd.logrotate
Source3:	pure-ftpd-xinetd
Source4:	pure-ftpd.service
Source6:        pure-ftpd.pam
Patch0:		pure-ftpd.mdkconf.patch
Provides:	ftp-server ftpserver
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Conflicts:	wu-ftpd, ncftpd, proftpd, anonftp, vsftpd
BuildRequires:	pam-devel
BuildRequires:	openldap-devel
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	openssl-devel

%description
Pure-FTPd is a fast, production-quality, standard-comformant FTP server,
based upon Troll-FTPd. Unlike other popular FTP servers, it has no known
security flaw, it is really trivial to set up and it is especially designed
for modern Linux and FreeBSD kernels (setfsuid, sendfile, capabilities) .
Features include PAM support, IPv6, chroot()ed home directories, virtual
domains, built-in LS, anti-warez system, bandwidth throttling, FXP, bounded
ports for passive downloads, UL/DL ratios, native LDAP and SQL support,
Apache log files and more.

%package 	anonymous
Summary:	Anonymous support for pure-ftpd
Group:		System/Servers
Requires:	pure-ftpd

%description 	anonymous
This package provides anonymous support for pure-ftpd. 

%package 	anon-upload
Summary:	Anonymous upload support for pure-ftpd
Group:		System/Servers
Requires:	pure-ftpd

%description 	anon-upload
This package provides anonymous upload support for pure-ftpd. 

%prep

%setup -q -n %{name}-%{version}
%patch0 -p1 -b .mdkconf

# nuke mac files
find -name "\._*" | xargs rm -f

cp %{SOURCE3} pure-ftpd-xinetd
cp %{SOURCE4} pure-ftpd.service
cp %{SOURCE6} pure-ftpd.pam

%build
%configure2_5x \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --with-paranoidmsg \
    --without-capabilities \
    --with-pam \
    --with-ldap \
    --with-mysql \
    --with-pgsql \
    --with-puredb \
    --without-sendfile \
    --with-altlog \
    --with-cookie \
    --with-diraliases \
    --with-throttling \
    --with-ratios \
    --with-quotas \
    --with-ftpwho \
    --with-welcomemsg \
    --with-uploadscript \
    --with-peruserlimits \
    --with-virtualhosts \
    --with-virtualchroot \
    --with-extauth \
    --with-largefile \
    --with-rfc2640 \
    --with-tls

%make

%install 
rm -rf %{buildroot}

%makeinstall_std

install -d -m 755 %{buildroot}%{_mandir}/man8/
install -d -m 755 %{buildroot}%{_sbindir}
install -d -m 755 %{buildroot}%{_sysconfdir}/rc.d/init.d/
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}

# Conf 
install -m 755 configuration-file/pure-config.pl %{buildroot}%{_sbindir}
install -m 644 configuration-file/pure-ftpd.conf %{buildroot}%{_sysconfdir}/%{name}
install -m 755 configuration-file/pure-config.py %{buildroot}%{_sbindir}
install -m 644 pureftpd-ldap.conf %{buildroot}%{_sysconfdir}/%{name}
install -m 644 pureftpd-mysql.conf %{buildroot}%{_sysconfdir}/%{name}
install -m 644 pureftpd-pgsql.conf %{buildroot}%{_sysconfdir}/%{name}

# Man
install -m 644 man/pure-ftpd.8 %{buildroot}%{_mandir}/man8
install -m 644 man/pure-ftpwho.8 %{buildroot}%{_mandir}/man8
install -m 644 man/pure-mrtginfo.8 %{buildroot}%{_mandir}/man8
install -m 644 man/pure-uploadscript.8 %{buildroot}%{_mandir}/man8
install -m 644 man/pure-pw.8 %{buildroot}%{_mandir}/man8
install -m 644 man/pure-pwconvert.8 %{buildroot}%{_mandir}/man8
install -m 644 man/pure-statsdecode.8 %{buildroot}%{_mandir}/man8
install -m 644 man/pure-quotacheck.8 %{buildroot}%{_mandir}/man8
install -m 644 man/pure-authd.8 %{buildroot}%{_mandir}/man8

install -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/pure-ftpd

# Pam 
install -d -m 755 %{buildroot}%{_sysconfdir}/pam.d/
install -m 0644 pure-ftpd.pam %{buildroot}%{_sysconfdir}/pam.d/%{name}

# Logrotate
install -d %{buildroot}%{_sysconfdir}/logrotate.d/
install -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

#anonymous ftp
mkdir -p %{buildroot}/var/ftp/pub/
mkdir -p %{buildroot}/var/ftp/incoming/

# xinetd support (tv)
mkdir -p %{buildroot}%{_sysconfdir}/xinetd.d
install -m0644 pure-ftpd-xinetd %{buildroot}%{_sysconfdir}/xinetd.d/pure-ftpd-xinetd

# avahi support (misc)
mkdir -p %{buildroot}%{_sysconfdir}/avahi/services/
install -m0644 pure-ftpd.service %{buildroot}%{_sysconfdir}/avahi/services/%{name}.service

%post
# ftpusers creation
if [ ! -f %{_sysconfdir}/ftpusers ]; then
	touch %{_sysconfdir}/ftpusers
fi

USERS="root bin daemon adm lp sync shutdown halt mail news uucp operator games nobody"
for i in $USERS ;do
    cat %{_sysconfdir}/ftpusers | grep -q "^$i$" || echo $i >> %{_sysconfdir}/ftpusers
done

%_post_service pure-ftpd

%pre
%_pre_useradd ftp /var/ftp /bin/false

%postun
%_postun_userdel ftp

%preun
%_preun_service pure-ftpd

%files
%doc FAQ THANKS README.Authentication-Modules README.Windows README.Virtual-Users README.Debian 
%doc README README.Contrib README.Configuration-File AUTHORS CONTACT HISTORY NEWS README.LDAP
%doc README.PGSQL README.MySQL pure-ftpd.png contrib/pure-vpopauth.pl
%doc contrib/pure-stat.pl pureftpd.schema
%attr(0755,root,root) %{_initrddir}/pure-ftpd

%config(noreplace) %{_sysconfdir}/%{name}/pure-ftpd.conf
%config(noreplace) %{_sysconfdir}/%{name}/pureftpd-ldap.conf
%config(noreplace) %{_sysconfdir}/%{name}/pureftpd-mysql.conf
%config(noreplace) %{_sysconfdir}/%{name}/pureftpd-pgsql.conf
%config(noreplace) %{_sysconfdir}/pam.d/pure-ftpd
%config(noreplace) %{_sysconfdir}/logrotate.d/pure-ftpd
%config(noreplace) %{_sysconfdir}/xinetd.d/pure-ftpd-xinetd
%config(noreplace) %{_sysconfdir}/avahi/services/%{name}.service

%{_bindir}/pure-pw
%{_bindir}/pure-pwconvert
%{_bindir}/pure-statsdecode
%{_sbindir}/pure-config.pl
%{_sbindir}/pure-config.py
%{_sbindir}/pure-ftpd
%{_sbindir}/pure-ftpwho
%{_sbindir}/pure-uploadscript
%{_sbindir}/pure-mrtginfo
%{_sbindir}/pure-quotacheck
%{_sbindir}/pure-authd

%attr(644,root,root) %{_mandir}/man8/*

%files anonymous
%dir /var/ftp/pub/

%files anon-upload
%attr(0777,root,root) %dir /var/ftp/incoming


%changelog
* Fri Mar 30 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.36-1
+ Revision: 788393
- 1.0.36

* Wed Dec 07 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.35-1
+ Revision: 738622
- 1.0.35
- various fixes

* Sat Nov 05 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.34-1
+ Revision: 720863
- 1.0.34
- various cleanups

* Tue May 03 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.32-1
+ Revision: 664156
- 1.0.32

* Sat Apr 30 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.31-1
+ Revision: 660789
- 1.0.31
- drop the mysql-5.5.10 fix, a similar fix was added upstream

* Fri Mar 18 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.30-1
+ Revision: 646420
- fix a silly typo :)
- P1: fix the build with latest mysql (Mikael Andersson)
- 1.0.30
- rebuilt against mysql-5.5.8 libs, again

* Mon Dec 27 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.29-4mdv2011.0
+ Revision: 625427
- rebuilt against mysql-5.5.8 libs

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.29-3mdv2011.0
+ Revision: 607240
- rebuild

* Wed Apr 07 2010 Funda Wang <fwang@mandriva.org> 1.0.29-2mdv2010.1
+ Revision: 532514
- rebuild

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.29-1mdv2010.1
+ Revision: 521045
- 1.0.29

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.28-3mdv2010.1
+ Revision: 511627
- rebuilt against openssl-0.9.8m

* Wed Feb 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.28-2mdv2010.1
+ Revision: 507039
- rebuild

* Tue Feb 09 2010 Frederik Himpe <fhimpe@mandriva.org> 1.0.28-1mdv2010.1
+ Revision: 503297
- update to new version 1.0.28

* Sat Dec 05 2009 Oden Eriksson <oeriksson@mandriva.com> 1.0.27-1mdv2010.1
+ Revision: 473775
- 1.0.27

  + Michael Scherer <misc@mandriva.org>
    - add support for tls

* Tue Nov 17 2009 Oden Eriksson <oeriksson@mandriva.com> 1.0.26-1mdv2010.1
+ Revision: 466903
- 1.0.26

* Sat Nov 07 2009 Oden Eriksson <oeriksson@mandriva.com> 1.0.24-1mdv2010.1
+ Revision: 462400
- 1.0.24

* Fri May 01 2009 Frederik Himpe <fhimpe@mandriva.org> 1.0.22-1mdv2010.0
+ Revision: 370252
- Update to new version 1.0.22
- Rediff configuration file patch

* Sat Dec 06 2008 Oden Eriksson <oeriksson@mandriva.com> 1.0.21-9mdv2009.1
+ Revision: 311205
- rebuilt against mysql-5.1.30 libs

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 1.0.21-8mdv2009.0
+ Revision: 225117
- rebuild

* Mon Dec 24 2007 Oden Eriksson <oeriksson@mandriva.com> 1.0.21-7mdv2008.1
+ Revision: 137491
- fix build (how did it ever build?)
- rebuilt against openldap-2.4.7 libs

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request
    - s/Mandrake/Mandriva/


* Wed Jan 10 2007 Oden Eriksson <oeriksson@mandriva.com> 1.0.21-6mdv2007.0
+ Revision: 107074
- Import pure-ftpd

* Wed Jan 10 2007 Oden Eriksson <oeriksson@mandriva.com> 1.0.21-6mdv2007.1
- bunzip sources and patches
- make it backportable for older pam

* Tue Sep 05 2006 Oden Eriksson <oeriksson@mandriva.com> 1.0.21-1mdv2007.0
- rebuilt against MySQL-5.0.24a-1mdv2007.0 due to ABI changes

* Mon Aug 14 2006 Oden Eriksson <oeriksson@mandriva.com> 1.0.21-4mdv2007.0
- misc spec fixes

* Sun Jun 25 2006 Jerome Soyer <saispo@mandriva.org> 1.0.21-3mdv2007.0
- Fix and close #23295

* Thu Jun 22 2006 Jerome Soyer <saispo@mandriva.org> 1.0.21-2mdv2007.0
- Add UTF8 support

* Fri Mar 03 2006 Michael Scherer <misc@mandriva.org> 1.0.21-1mdk
- new version
- use mkrel
- add avahi service description file
- rpmbuildupdatable, with correct url

* Sun Oct 30 2005 Oden Eriksson <oeriksson@mandriva.com> 1.0.20-8mdk
- rebuilt against MySQL-5.0.15

* Wed Aug 31 2005 Buchan Milne <bgmilne@linux-mandrake.com> 1.0.20-7mdk
- Rebuild for libldap2.3

* Tue May 10 2005 Buchan Milne <bgmilne@linux-mandrake.com> 1.0.20-6mdk
- Rebuild for postgresql-devel 8.0.2

* Tue Feb 08 2005 Buchan Milne <bgmilne@linux-mandrake.com> 1.0.20-5mdk
- rebuild for ldap2.2_7

* Fri Feb 04 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 1.0.20-4mdk
- rebuilt against new openldap libs

* Tue Jan 25 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 1.0.20-3mdk
- rebuilt against MySQL-4.1.x and PostgreSQL-8.x system libs

* Tue Jul 27 2004 Pascal Terjan <pterjan@mandrake.org> 1.0.20-2mdk
- Enable large file support
- Drop useless provide pure-ftpd

* Tue Jul 27 2004 Pascal Terjan <pterjan@mandrake.org> 1.0.20-1mdk
- 1.0.20

* Tue Apr 20 2004 Laurent Culioli <laurent@mandrake.org> 1.0.18-1mdk
- 1.0.18

