import sys
import threading
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from twisted.application import service
from twisted.internet.endpoints import serverFromString
from twisted.internet.protocol import ServerFactory
from twisted.python.components import registerAdapter
from twisted.python import log
from ldaptor.inmemory import fromLDIFFile
from ldaptor.interfaces import IConnectedLDAPEntry
from ldaptor.protocols.ldap import ldaperrors
from ldaptor.protocols.ldap.ldapserver import LDAPServer
from ldaptor.protocols import pureldap
from twisted.internet import defer, ssl
from twisted.internet import reactor


config1 = b"""\
dn: dc=com
dc: com
objectClass: dcObject

dn: dc=calibreweb,dc=com
dc: calibreweb
objectClass: dcObject
objectClass: organization

dn: ou=people,dc=calibreweb,dc=com
objectClass: organizationalUnit
ou: people

dn: cn=root,dc=calibreweb,dc=com
cn: root
gn: root
mail: admin@calibreweb.com
objectclass: top
objectclass: person
objectClass: inetOrgPerson
sn: admin
userPassword: secret

dn: uid=user0,ou=people,dc=calibreweb,dc=com
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: user0
cn: user0
gn: John
sn: Doe
userPassword: terces

dn: uid=user1,ou=people, dc=calibreweb,dc=com
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: user1
cn: user1
gn: John
sn: Smith
userPassword: eekretsay

"""

config2 = b"""\
dn: dc=com
dc: com
objectClass: dcObject

dn: dc=calibreweb,dc=com
dc: calibreweb
objectClass: dcObject
objectClass: organization

dn: ou=people,dc=calibreweb,dc=com
objectClass: organizationalUnit
ou: people

dn: cn=root,dc=calibreweb,dc=com
cn: root
gn: root
mail: admin@calibreweb.com
objectclass: top
objectclass: person
objectClass: inetOrgPerson
sn: admin
userPassword: secret

dn: uid=user0,ou=people,dc=calibreweb,dc=com
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: user0
gn: John
sn: Doe
userPassword: terces

dn: uid=user1,ou=people, dc=calibreweb,dc=com
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: user1
gn: John
sn: Smith
userPassword: eekretsay

"""

config3 = b"""\
dn: dc=com
dc: com
objectClass: dcObject

dn: dc=calibreweb,dc=com
dc: calibreweb
objectClass: dcObject
objectClass: organization

dn: ou=people,dc=calibreweb,dc=com
objectClass: organizationalUnit
ou: people

dn: cn=root,dc=calibreweb,dc=com
cn: root
gn: root
mail: admin@calibreweb.com
objectclass: top
objectclass: person
objectClass: inetOrgPerson
sn: admin
userPassword: secret

dn: uid=user0,ou=people,dc=calibreweb,dc=com
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: user0
gn: John
sn: Doe
userPassword: terces

dn: uid=user1,ou=people, dc=calibreweb,dc=com
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: user1
gn: John
sn: Smith
userPassword: eekretsay

"""

class Tree(object):

    def __init__(self, config=0):
        global config1, config2, config3
        if config == 1:
            LDIF = config1
        if config == 2:
            LDIF = config2
        if config == 3:
            LDIF = config3
        self.f = BytesIO(LDIF)
        d = fromLDIFFile(self.f)
        d.addCallback(self.ldifRead)

    def ldifRead(self, result):
        self.f.close()
        self.db = result

class LDAPSTARTTLSServer(LDAPServer):
    """
    An STARTtTLS LDAP server proxy.
    """

    unbound = False
    use_tls = False

    def __init__(self):
        LDAPServer.__init__(self)
        self.startTLS_initiated = False

    def handle_LDAPBindRequest(self, request, controls, reply):
        if not self.startTLS_initiated and self.use_tls:
            # raise ldaperrors.LDAPStrongAuthRequired()
            # log.msg('Wrong binding')
            raise ldaperrors.LDAPConfidentialityRequired()
        else:
            return LDAPServer.handle_LDAPBindRequest(self, request, controls, reply)

    def handle_LDAPUnBindRequest(self, request, controls, reply):
        self.startTLS_initiated = False
        return LDAPServer.handle_LDAPUnbindRequest(self, request, controls, reply)

    def handle_LDAPExtendedRequest(self, request, controls, reply):
        """
        Handler for extended LDAP requests (e.g. startTLS).
        """
        if self.debug:
            log.msg("Received extended request: " + request.requestName.decode('utf-8'))
        if request.requestName == pureldap.LDAPStartTLSRequest.oid:
            d = defer.maybeDeferred(self.handleStartTLSRequest, request, controls, reply)
            d.addErrback(log.err)
            return d
        return self.handleUnknown(request, controls, reply)

    def handleStartTLSRequest(self, request, controls, reply):
        """
        If the protocol factory has an `options` attribute it is assumed
        to be a `twisted.internet.ssl.CertificateOptions` that can be used
        to initiate TLS on the transport.
        Otherwise, this method returns an `unavailable` result code.
        """

        if self.debug:
            log.msg("Received startTLS request: " + repr(request))
        if hasattr(self.factory, 'options'):
            if self.startTLS_initiated:
                msg = pureldap.LDAPStartTLSResponse(
                    resultCode=ldaperrors.LDAPOperationsError.resultCode)
                log.msg(
                    "Session already using TLS.  "
                    "Responding with 'operationsError' (1): " + repr(msg))
            else:
                if self.debug:
                    log.msg("Setting success result code ...")
                msg = pureldap.LDAPStartTLSResponse(
                    resultCode=ldaperrors.Success.resultCode)
                if self.debug:
                    log.msg("Replying with successful LDAPStartTLSResponse ...")
                reply(msg)
                if self.debug:
                    log.msg("Initiating startTLS on transport ...")
                self.transport.startTLS(self.factory.options)
                self.startTLS_initiated = True
                msg = None
        else:
            msg = pureldap.LDAPStartTLSResponse(
                resultCode=ldaperrors.LDAPUnavailable.resultCode)
            log.msg(
                "StartTLS not implemented.  "
                "Responding with 'unavailable' (52): " + repr(msg))
        return defer.succeed(msg)

class LDAPServerFactory(ServerFactory):
    protocol = LDAPServer

    def __init__(self, root, tls):
        self.root = root
        self.use_TLS = tls

    def buildProtocol(self, addr):
        proto = LDAPSTARTTLSServer()
        proto.debug = self.debug
        proto.use_tls = self.use_TLS
        proto.factory = self
        return proto

class TestLDApServer(threading.Thread):
    def __init__(self, port=8080, encrypt=None, config=0):
        threading.Thread.__init__(self)
        self.is_running=False
        tls = False
        cert = None
        # First of all, to show logging info in stdout :
        # log.startLogging(sys.stderr)
        # We initialize our tree
        tree = Tree(config)

        registerAdapter(
            lambda x: x.root,
            LDAPServerFactory,
            IConnectedLDAPEntry)

        if encrypt == 'SSL':
            serverEndpointStr = "ssl:{0}:privateKey=./SSL/ssl.key:certKey=./SSL/ssl.crt".format(port)
        else:
            if encrypt == 'TLS':
                tls = True
                cert = ssl.DefaultOpenSSLContextFactory('./SSL/ssl.key', './SSL/ssl.crt')
            serverEndpointStr = "tcp:{0}".format(port)
        factory = LDAPServerFactory(tree.db, tls)
        if cert:
            factory.options = cert
        factory.debug = True
        e = serverFromString(reactor, serverEndpointStr)
        e.listen(factory)
        self.serv = reactor

    def is_running(self):
        return self.is_running

    def run(self):
        self.is_running = True
        self.serv.run(installSignalHandlers=False)

    def stop_LdapServer(self):
        self.is_running = False
        reactor.callFromThread(reactor.stop)

