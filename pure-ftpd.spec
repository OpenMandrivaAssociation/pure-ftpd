Summary:	Lightweight, fast and secure FTP server
Name:		pure-ftpd
Version:	1.0.36
Release:	5
License:	GPLv2
Group:		System/Servers
Url:		http://www.pureftpd.org
Source0:	http://download.pureftpd.org/pub/pure-ftpd/releases/%{name}-%{version}.tar.gz
Source1:	pure-ftpd.init
Source2:	pure-ftpd.logrotate
Source3:	pure-ftpd-xinetd
Source4:	pure-ftpd.service
Source6:	pure-ftpd.pam
Patch0:		pure-ftpd.mdkconf.patch
BuildRequires:	mysql-devel
BuildRequires:	pam-devel
BuildRequires:	openldap-devel
BuildRequires:	postgresql-devel
BuildRequires:	pkgconfig(openssl)
Requires(post,preun,pre,postun):	rpm-helper
Provides:	ftp-server
Provides:	ftpserver
Conflicts:	anonftp
Conflicts:	ncftpd
Conflicts:	proftpd
Conflicts:	vsftpd
Conflicts:	wu-ftpd

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

%setup -q
%apply_patches

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

