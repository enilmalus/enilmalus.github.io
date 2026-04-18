---
title: LDAP
date: 2026-04-15T10:00:00+08:00
draft: false
toc: true
images:
tags:
  - Hack
---
## LDAPsearch

### LDAP 探测

执行 LDAP 匿名探测。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ ldapsearch -x -H ldap://10.129.95.210 -s base namingcontexts                                                                                                                   
# extended LDIF
#
# LDAPv3
# base <> (default) with scope baseObject
# filter: (objectclass=*)
# requesting: namingcontexts 
#

#
dn:
namingContexts: DC=htb,DC=local
namingContexts: CN=Configuration,DC=htb,DC=local
namingContexts: CN=Schema,CN=Configuration,DC=htb,DC=local
namingContexts: DC=DomainDnsZones,DC=htb,DC=local
namingContexts: DC=ForestDnsZones,DC=htb,DC=local

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1

```

允许匿名绑定，进一步枚举。

```bash
┌──(kali㉿kali)-[~/Work/Kali/Forest]
└─$ ldapsearch -x -H ldap://10.129.95.210 -b "DC=htb,DC=local" "(objectClass=user)" sAMAccountName description userAccountControl memberOf         
# extended LDIF
#
# LDAPv3
# base <DC=htb,DC=local> with scope subtree
# filter: (objectClass=user)
# requesting: sAMAccountName description userAccountControl memberOf 
#

# Guest, Users, htb.local
dn: CN=Guest,CN=Users,DC=htb,DC=local
description: Built-in account for guest access to the computer/domain
memberOf: CN=Guests,CN=Builtin,DC=htb,DC=local
userAccountControl: 66082
sAMAccountName: Guest

# DefaultAccount, Users, htb.local
dn: CN=DefaultAccount,CN=Users,DC=htb,DC=local
description: A user account managed by the system.
memberOf: CN=System Managed Accounts Group,CN=Builtin,DC=htb,DC=local
userAccountControl: 66082
sAMAccountName: DefaultAccount

# FOREST, Domain Controllers, htb.local
dn: CN=FOREST,OU=Domain Controllers,DC=htb,DC=local
userAccountControl: 532480
sAMAccountName: FOREST$

# EXCH01, Computers, htb.local
dn: CN=EXCH01,CN=Computers,DC=htb,DC=local
memberOf: CN=Exchange Install Domain Servers,CN=Microsoft Exchange System Obje
 cts,DC=htb,DC=local
memberOf: CN=Managed Availability Servers,OU=Microsoft Exchange Security Group
 s,DC=htb,DC=local
memberOf: CN=Exchange Trusted Subsystem,OU=Microsoft Exchange Security Groups,
 DC=htb,DC=local
memberOf: CN=Exchange Servers,OU=Microsoft Exchange Security Groups,DC=htb,DC=
 local
userAccountControl: 4096
sAMAccountName: EXCH01$

# Exchange Online-ApplicationAccount, Users, htb.local
dn: CN=Exchange Online-ApplicationAccount,CN=Users,DC=htb,DC=local
userAccountControl: 546
sAMAccountName: $331000-VK4ADACQNUCA

# SystemMailbox{1f05a927-89c0-4725-adca-4527114196a1}, Users, htb.local
dn: CN=SystemMailbox{1f05a927-89c0-4725-adca-4527114196a1},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_2c8eef0a09b545acb

# SystemMailbox{bb558c35-97f1-4cb9-8ff7-d53741dc928c}, Users, htb.local
dn: CN=SystemMailbox{bb558c35-97f1-4cb9-8ff7-d53741dc928c},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_ca8c2ed5bdab4dc9b

# SystemMailbox{e0dc1c29-89c3-4034-b678-e6c29d823ed9}, Users, htb.local
dn: CN=SystemMailbox{e0dc1c29-89c3-4034-b678-e6c29d823ed9},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_75a538d3025e4db9a

# DiscoverySearchMailbox {D919BA05-46A6-415f-80AD-7E09334BB852}, Users, htb.loc
 al
dn: CN=DiscoverySearchMailbox {D919BA05-46A6-415f-80AD-7E09334BB852},CN=Users,
 DC=htb,DC=local
userAccountControl: 514
sAMAccountName: SM_681f53d4942840e18

# Migration.8f3e7716-2011-43e4-96b1-aba62d229136, Users, htb.local
dn: CN=Migration.8f3e7716-2011-43e4-96b1-aba62d229136,CN=Users,DC=htb,DC=local
userAccountControl: 514
sAMAccountName: SM_1b41c9286325456bb

# FederatedEmail.4c1f4d8b-8179-4148-93bf-00a95fa1e042, Users, htb.local
dn: CN=FederatedEmail.4c1f4d8b-8179-4148-93bf-00a95fa1e042,CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_9b69f1b9d2cc45549

# SystemMailbox{D0E409A0-AF9B-4720-92FE-AAC869B0D201}, Users, htb.local
dn: CN=SystemMailbox{D0E409A0-AF9B-4720-92FE-AAC869B0D201},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_7c96b981967141ebb

# SystemMailbox{2CE34405-31BE-455D-89D7-A7C7DA7A0DAA}, Users, htb.local
dn: CN=SystemMailbox{2CE34405-31BE-455D-89D7-A7C7DA7A0DAA},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_c75ee099d0a64c91b

# SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9}, Users, htb.local
dn: CN=SystemMailbox{8cc370d3-822a-4ab8-a926-bb94bd0641a9},CN=Users,DC=htb,DC=
 local
userAccountControl: 514
sAMAccountName: SM_1ffab36a2f5f479cb

# HealthMailboxc3d7722415ad41a5b19e3e00e165edbe, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxc3d7722415ad41a5b19e3e00e165edbe,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxc3d7722

# HealthMailboxfc9daad117b84fe08b081886bd8a5a50, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxfc9daad117b84fe08b081886bd8a5a50,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxfc9daad

# HealthMailboxc0a90c97d4994429b15003d6a518f3f5, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxc0a90c97d4994429b15003d6a518f3f5,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxc0a90c9

# HealthMailbox670628ec4dd64321acfdf6e67db3a2d8, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox670628ec4dd64321acfdf6e67db3a2d8,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox670628e

# HealthMailbox968e74dd3edb414cb4018376e7dd95ba, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox968e74dd3edb414cb4018376e7dd95ba,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox968e74d

# HealthMailbox6ded67848a234577a1756e072081d01f, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox6ded67848a234577a1756e072081d01f,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox6ded678

# HealthMailbox83d6781be36b4bbf8893b03c2ee379ab, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox83d6781be36b4bbf8893b03c2ee379ab,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox83d6781

# HealthMailboxfd87238e536e49e08738480d300e3772, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxfd87238e536e49e08738480d300e3772,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxfd87238

# HealthMailboxb01ac647a64648d2a5fa21df27058a24, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailboxb01ac647a64648d2a5fa21df27058a24,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailboxb01ac64

# HealthMailbox7108a4e350f84b32a7a90d8e718f78cf, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox7108a4e350f84b32a7a90d8e718f78cf,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox7108a4e

# HealthMailbox0659cc188f4c4f9f978f6c2142c4181e, Monitoring Mailboxes, Microsof
 t Exchange System Objects, htb.local
dn: CN=HealthMailbox0659cc188f4c4f9f978f6c2142c4181e,CN=Monitoring Mailboxes,C
 N=Microsoft Exchange System Objects,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: HealthMailbox0659cc1

# Sebastien Caron, Exchange Administrators, Information Technology, Employees, 
 htb.local
dn: CN=Sebastien Caron,OU=Exchange Administrators,OU=Information Technology,OU
 =Employees,DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: sebastien

# Lucinda Berger, IT Management, Information Technology, Employees, htb.local
dn: CN=Lucinda Berger,OU=IT Management,OU=Information Technology,OU=Employees,
 DC=htb,DC=local
userAccountControl: 66048
sAMAccountName: lucinda

# Andy Hislip, Helpdesk, Information Technology, Employees, htb.local
dn: CN=Andy Hislip,OU=Helpdesk,OU=Information Technology,OU=Employees,DC=htb,D
 C=local
userAccountControl: 66048
sAMAccountName: andy

# Mark Brandt, Sysadmins, Information Technology, Employees, htb.local
dn: CN=Mark Brandt,OU=Sysadmins,OU=Information Technology,OU=Employees,DC=htb,
 DC=local
userAccountControl: 66048
sAMAccountName: mark

# Santi Rodriguez, Developers, Information Technology, Employees, htb.local
dn: CN=Santi Rodriguez,OU=Developers,OU=Information Technology,OU=Employees,DC
 =htb,DC=local
userAccountControl: 66048
sAMAccountName: santi

# search reference
ref: ldap://ForestDnsZones.htb.local/DC=ForestDnsZones,DC=htb,DC=local

# search reference
ref: ldap://DomainDnsZones.htb.local/DC=DomainDnsZones,DC=htb,DC=local

# search reference
ref: ldap://htb.local/CN=Configuration,DC=htb,DC=local

# search result
search: 2
result: 0 Success

# numResponses: 34
# numEntries: 30
# numReferences: 3

```

扫描结果暴露出许多人名，建立一个 `users.txt`，将他们存放进去。