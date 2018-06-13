# STEP 0: Install missing SVN packages

```
sudo apt-get install git-svn
sudo apt-get install subversion libapache2-svn 
```

# STEP 1:  Preparing Credentials

## Option1: Enter manually credentials

Clone something from target repository to enter credentials manually once.

Example:
```

⟩ svn checkout http://svn-ldc/svn/Controls/trunk/Linux/CommonComponents
Authentication realm: <http://svn-ldc:80> svn-ldc repository access
Password for 'osboxes': *****************

Authentication realm: <http://svn-ldc:80> svn-ldc repository access
Username: Brosche@lenze.com
Password for 'Brosche@lenze.com': *****************

````

## Option 2: Generate credentials

1. Generate the MD5 hash of the realmstring of the repository provider. If you host your own with VisualSVN, it will be something similar to: <https://cde274933.lenze.com:443> VisualSVN Server
2. Create a file under /home/<username>/.subversion/auth/svn.simple, where the filename is the md5 hash. This is how git svn will find the credentials when challenged.
3. The content of the file will have key value pairs as shown below:

K 8
passtype
V 6
simple
K 8
password
V <password character count>
<password>
K 15
svn:realmstring
V 50
<https://cde274933.lenze.com:443> VisualSVN Server
K 8
username
V <username character count>
<username>
END

4. Now both git svn and svn should be able to check out from the repo without asking for credentials.

# STEP 2: Preparing gitman.yml

In a project, such as waf-prototyping, add an svn entry. Example below:

Example:
```
location: imports

sources:
- name: TAs
  type: git-svn
  repo: http://svn-ldc/svn/Controls/trunk/XP/TAs/Implementation/i900/Bootprojects/51/51_soc/
  rev: HEAD

- name: lz4
  type: git
  repo: https://github.com/lz4/lz4
  rev: v1.8.1.2

```

By default the `type` is `git`.

It is important to note that if the mentioned revision does not exist, gitman will not throw errors, because git svn will not throw errors.

