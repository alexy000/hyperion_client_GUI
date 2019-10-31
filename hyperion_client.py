"""
hyperion_client.py module.

Connect to the hyperion json interface and send/receive messages.
"""
import json
import socket
import time


class hyperion_client:
    """Hyperion JSON interface client class."""

    def __init__(self, host='127.0.0.1', port=19444):
        """
        Hyperion_client initializer.

        :param host: ip address of the host
        :param port: port number
        """
        self._host = str(host)
        self._port = int(port)
        self.__socket = socket.socket()
        self._connected = False

# -IP-
    @property
    def host(self):
        """
        Return ip address.

        :return: ip address of the hyperion server host
        """
        return self._host

    @host.setter
    def host(self, host):
        """
        Set ip address.

        :param host: ip address of the hyperion server host
        """
        self._host = str(host)

# -PORT-
    @property
    def port(self):
        """
        Return port.

        :return: port of the hyperion server host
        """
        return self._port

    @port.setter
    def port(self, port):
        """
        Set port.

        :param port: port of the hyperion server host
        """
        self._port = int(port)

# -SOCKET-
# @property
# def socket(self):
# return self.__socket
##
# @socket.setter
# def socket(self, socket):
#       self.__socket = socket

# -CONNECTION-
    @property
    def connected(self):
        """
        Return connection status.

        :return: boolean value of the connection status. True if connected
        """
        return self._connected

# @connected.setter
# def connected(self, state):
#       self._connected = state

    def open_connection(self, timeout=10):
        """
        Open a socket connection to the server.

        :param timeout: timeout in seconds
        """
        if self._connected:
            return
        self.__socket.settimeout(timeout)
        try:
            self.__socket.connect((self._host, self._port))
            self._connected = True
        except socket.error as exc:
            print("Error during connection to ", self._host, ":", self._port)
            raise exc

    def close_connection(self, clean=False):
        """
        Close socket connection to the server.

        :param clean: if True -> clear all the effects/color on disconnection
        """
        if self._connected:
            try:
                if clean:
                    self.__socket.send('{"command":"clearall"}\n'.encode('utf-8'))
                self.__socket.close()
            except socket.error as exc:
                print("Could not close socket connection\nMessage: ", exc)

    def recv_timeout(self, timeout=2):
        """Receive data from socket.

        :param timeout: time period to wait when waiting for hyperion server
        :return: the received string
        """
        # make socket non blocking
        self.__socket.setblocking(0)
        # total data partwise in an array
        total_data = []
        data = ''
        # beginning time
        begin = time.time()
        while 1:
            # if you got some data, then break after timeout
            if total_data and time.time() - begin > timeout:
                break
            # if you got no data at all, wait twice the timeout
            elif time.time() - begin > timeout * 2:
                break
            # recv something
            try:
                data = self.__socket.recv(8192)
                if data:
                    total_data.append(data.decode("utf-8"))
                    # change the beginning time for measurement
                    begin = time.time()
                else:
                    # sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass
        # join all parts to make final string
        return ''.join(total_data)

    def test_connection(self):
        """
        Open socket connection to the server (if not already open).

        :return: boolean value of the connection status. True if connected
        """
        if not self._connected:
            print("Not connected to Hyperion server: autoconnecting...")
            self.open_connection()
        return self._connected

    def send_message(self, message):
        """Send data to socket.

        :param message: json-formatted message
        """
        try:
            self.__socket.sendall(message.encode('utf-8'))
        except socket.error as exc:
            print("Error while sending the data\nMessage: ", exc)

###############################################################################

    def response_serverinfo(self):
        """
        Get responses to the latest commands sent and all the other infos from the hyperion json server.

        :return: json structure containing infos from the hyperion json server
        """
        if not self.test_connection():
            return
        resp = ''
        # create a message to send
        message = '{"command":"serverinfo"}\n'
        self.send_message(message)
        try:
            resp = self.recv_timeout()
        except socket.error as exc:
            print("Error while receiving the data\nMessage: ", exc)
        return resp

    def serverinfo(self):
        """
        Get informations from the hyperion json server.

        :return: json structure containing infos from the hyperion json server
        """
        resp = self.response_serverinfo()
        info = resp[resp.find('{"info":{'):]
        parsed = json.loads(info)
        return parsed

    def effects(self):
        """
        Get all the effects from the hyperion json server.

        :return: json structure containing all the effects from hyperion.
        """
        return self.serverinfo()["info"]["effects"]

    def effects_names(self):
        """
        Get the name of all the effects from hyperion.

        :return: array of effects names
        """
        effects_name = []
        effects_list = self.effects()
        for e in effects_list:
            effects_name.append(str(e["name"]))
        return effects_name

    def active_effects(self):
        """
        Get all the active effects from hyperion.

        :return: json structure containing all the active effects
        """
        return self.serverinfo()["info"]["activeEffects"]

    def active_effects_names(self):
        """
        Get the name of all the active effects from hyperion.

        :return: array of active effects names
        """
        effect_list = []
        priority_list = []
        parsed = self.serverinfo()
        activeEffects = parsed["info"]["activeEffects"]
        if activeEffects:
            for i in range(len(activeEffects)):
                args = activeEffects[i]["args"]
                path = activeEffects[i]["script"]
                for e in parsed["info"]["effects"]:
                    if (e["args"] == args) and (e["script"] == path):
                        effect_list.append(str(e["name"]))
                        priority_list.append(int(activeEffects[i]["priority"]))
            if len(effect_list) != len(activeEffects):
                s = json.dumps(activeEffects, indent=4, sort_keys=True)
                raise NameError("Cannot find a name for some of the current effects\nYou may be using custom args\n", s)
        return effect_list

    def active_color(self, mode=None):
        """
        Get the active color from hyperion.

        :param mode: format of the color ("RGB", "HEX", "HLS"). No param or falsey param = all the formats
        :return: color value or list of color values
        """
        activeColor = self.serverinfo()["info"]["activeLedColor"]
        if activeColor:
            if str(mode) == "RGB":
                return self.active_color()[0]["RGB Value"]
            elif str(mode) == "HEX":
                return self.active_color()[0]["HEX Value"]
            elif str(mode) == "HLS":
                return self.active_color()[0]["HLS Value"]
        return activeColor

    # def current():

    def transform(self):
        """
        Get the transform values from hyperion.

        :return: json structure containing transform values
        """
        return self.serverinfo()["info"]["transform"]

    def temperature(self):
        """
        Get the temperature values from hyperion.

        :return: json structure containing temperature values
        """
        return self.serverinfo()["info"]["temperature"]

    def adjustment(self):
        """
        Get the adjustment values from hyperion.

        :return: json structure containing adjustment values
        """
        return self.serverinfo()["info"]["adjustment"]

    def correction(self):
        """
        Get the correction values from hyperion.

        :return: json structure containing correction values
        """
        return self.serverinfo()["info"]["correction"]

    def priorities(self):
        """
        Get the property values from hyperion.

        :return: json structure containing priority values
        """
        return self.serverinfo()["info"]["priorities"]

    def hostname(self):
        """
        Get the hostname from hyperion.

        :return: name of the host of hyperion
        """
        return self.serverinfo()["info"]["hostname"]

    def hyperion_build(self):
        """
        Get the hyperion build info from hyperion.

        :return: name of the host of hyperion
        """
        return self.serverinfo()["info"]["hyperion_build"]

###############################################################################

    def set_RGBcolor(self, red, green, blue, priority=100, duration=0):
        """
        Send effect to the hyperion json server.

        :param red: red value in RGB format [0-255]
        :param green: green value in RGB format [0-255]
        :param blue: blue value in RGB format [0-255]
        :param priority: priority value
        :param duration: duration in milliseconds
        """
        if not self.test_connection():
            return
        # create a message to send
        message = '{"command":"color", "priority":' + str(priority) + ', '
        message += '"color":[' + str(red) + ',' + str(green) + ',' + str(blue) + ']'
        if duration > 0:
            message += ', "duration":' + str(duration)
        message += '}\n'
        print(message)
        self.send_message(message)

    def set_effect(self, effectName, priority=100, effectArgs=None, duration=0):
        """
        Send effect to the hyperion json server.

        :param effectName: Name of the effect
        :param priority: priority value
        :param effectArgs: Custom arguments for the effect
        :param duration: duration in milliseconds
        """
        if not self.test_connection():
            return
        # create a message to send
        message = '{"command":"effect","effect":{"name":"' + str(effectName)
        if effectArgs:
            message += '", "args":' + str(effectArgs)
        message += '"},"priority":' + str(priority)
        if duration > 0:
            message += ', "duration":' + str(duration)
        message += '}\n'
        print(message)
        self.send_message(message)

    def clear(self, priority=100):
        """
        Clear the highest priority effect/color (with lower priority value).

        :param priority: clear priority value
        """
        if not self.test_connection():
            return
        # create a message to send
        message = '{"command":"clear","priority":' + priority + '}\n'
        self.send_message(message)

    def clear_all(self):
        """Clear all the effects/color."""
        if not self.test_connection():
            return
        # create a message to send
        message = '{"command":"clearall"}\n'
        self.send_message(message)

    def set_image(self, image_data, width, height, priority=100, duration=0):
        """
        Set leds to the color of the image border.

        :param image_data: base64 RGB888 image data
        :param width: width of the image
        :param height: height of the image
        :param priority: priority value
        :param duration: duration in milliseconds
        """
        if not self.test_connection():
            return
        # create a message to send
        message = '{"command":"image","imagewidth":' + str(width)
        message += ',"imageheight":' + str(height)
        message += ',"imagedata":' + str(image_data)
        message += ',"priority":' + str(priority)
        if duration > 0:
            message += ', "duration":' + str(duration)
        message += '}\n'
        # print(message)
        self.send_message(message)

    def set_transform(self, identifier, blacklevel, gamma, luminanceGain, luminanceMinimum, saturationGain, saturationLGain, threshold, valueGain, whitelevel):
        """
        Send the transform values to the hyperion json server.

        :param identifier: transform id for the hyperion server to identify it
        :param blacklevel: black level value
        :param gamma: gamma value
        :param luminanceGain: luminance gain value
        :param luminanceMinimum: luminance minimum value
        :param saturationGain: saturation gain value
        :param saturationLGain: saturationLGain value
        :param threshold: threshold
        :param valueGain: value gain
        :param whitelevel: white level value
        :return:
        """
        if not self.test_connection():
            return
        # create a message to send
        message = '{"command":"transform","transform":{'
        message += '"blacklevel":[' + str(blacklevel[0]) + ',' + str(blacklevel[1]) + ',' + str(blacklevel[2])
        message += '],"gamma":[' + str(gamma[0]) + ',' + str(gamma[1]) + ',' + str(gamma[2])
        message += '],"id":"' + str(identifier)
        message += '","luminanceGain:"' + str(luminanceGain) + ''
        message += ',"luminanceMinimum:"' + str(luminanceMinimum) + ''
        message += ',"saturationGain:"' + str(saturationGain) + ''
        message += ',"saturationLGain:"' + str(saturationLGain) + ''
        message += '],"threshold":[' + str(threshold[0]) + ',' + str(threshold[1]) + ',' + str(threshold[2])
        message += '],"valueGain:"' + str(valueGain) + ''
        message += '],"whitelevel":[' + str(whitelevel[0]) + ',' + str(whitelevel[1]) + ',' + str(whitelevel[2])
        message += '}}\n'
        # print(message)
        self.send_message(message)

    def set_correction(self, identifier, red, green, blue):
        """
        Send the correction values to the hyperion json server.

        :param identifier: correction's id for the hyperion server to identify it
        :param red: red value in RGB format [0-255]
        :param green: green value in RGB format [0-255]
        :param blue: blue value in RGB format [0-255]
        """
        if not self.test_connection():
            return
        # create a message to send
        message = '{"command":"correction","correction":{'
        message += '"correctionValues":[' + str(red) + ',' + str(green) + ',' + str(blue)
        message += '],"id":"' + str(identifier)
        message += '"}}\n'
        # print(message)
        self.send_message(message)

    def set_temperature(self, identifier, red, green, blue):
        """
        Send the temperature values to the hyperion json server.

        :param identifier: temperature's id for the hyperion server to identify it
        :param red: red value in RGB format [0-255]
        :param green: green value in RGB format [0-255]
        :param blue: blue value in RGB format [0-255]
        """
        if not self.test_connection():
            return
        # create a message to send
        message = '{"command":"temperature","temperature":{'
        message += '"correctionValues":[' + str(red) + ',' + str(green) + ',' + str(blue)
        message += '],"id":"' + str(identifier)
        message += '"}}\n'
        # print(message)
        self.send_message(message)

    def set_adjustment(self, identifier, redAdjust, greenAdjust, blueAdjust):
        """
        Send the adjustment values to the hyperion json server.

        :param identifier: adjustment's id for the hyperion server to identify it
        :param redAdjust: value of the red adjustment in RGB format [0-255]
        :param greenAdjust: value of the green adjustment in RGB format [0-255]
        :param blueAdjust: value of the blue adjustment in RGB format [0-255]
        """
        if not self.test_connection():
                        return
        # create a message to send
        message = '{"command":"adjustment","adjustment":{"id":"' + str(identifier)
        message += '","redAdjust":[' + str(redAdjust[0]) + ',' + str(redAdjust[1]) + ',' + str(redAdjust[2])
        message += '],"greenAdjust":[' + str(greenAdjust[0]) + ',' + str(greenAdjust[1]) + ',' + str(greenAdjust[2])
        message += '],"blueAdjust":[' + str(blueAdjust[0]) + ',' + str(blueAdjust[1]) + ',' + str(blueAdjust[2])
        message += ']}}\n'
        # print(message)
        self.send_message(message)

    def send_led_data(self, led_data, priority=100, duration=0):
        """
        Send the led data in a message format that hyperion can understand.

        :param led_data: bytearray of the led data (r,g,b) * hyperion.ledcount
        :param priority: priority value
        :param duration: duration in milliseconds
        """
        if not self.test_connection():
            return
        # create a message to send
        message = '{"color":['
        # add all the color values to the message
        for i in range(len(led_data)):
            message += repr(led_data[i])
            # separate the color values with ",", but not at the end
            if not i == len(led_data) - 1:
                message += ','
        # complete message
        message += '],"command":"color","priority":' + str(priority)
        if duration > 0:
            message += ', "duration":' + str(duration)
        message += '}\n'
        # print message
        self.send_message(message)
