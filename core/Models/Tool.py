"""Tool Model. A tool is an instanciation of a command against a target"""

from core.Models.Element import Element
from core.Components.mongo import MongoCalendar
from bson.objectid import ObjectId
from datetime import datetime
import core.Components.Utils as Utils
import re

class Tool(Element):
    """
    Represents a Tool object that defines a tool. A tool is a command run materialized on a runnable object (wave, scope, ip, or port)

    Attributes:
        coll_name: collection name in pollenisator database
    """
    coll_name = "tools"

    def __init__(self, valuesFromDb=None):
        """Constructor
        Args:
            valueFromDb: a dict holding values to load into the object. A mongo fetched interval is optimal.
                        possible keys with default values are : _id(None), parent(None), tags([]), infos({}),
                        name(""), wave(""), scope(""), ip(""), port(""), proto("tcp"), lvl(""), text(""), dated("None"),
                        datef("None"), scanner_ip("None"), status([]), notes(""), resultfile("")
        """
        if valuesFromDb is None:
            valuesFromDb = {}
        super().__init__(valuesFromDb.get("_id", None), valuesFromDb.get("parent", None), valuesFromDb.get(
            "tags", []), valuesFromDb.get("infos", {}))
        self.datef = "None"
        self.dated = "None"
        self.scanner_ip = "None"
        self.resultfile = ""
        self.status = []
        self.initialize(valuesFromDb.get("name", ""), valuesFromDb.get("wave", ""),
                        valuesFromDb.get(
                            "scope", ""), valuesFromDb.get("ip", ""),
                        str(valuesFromDb.get("port", "")), valuesFromDb.get(
                            "proto", "tcp"),
                        valuesFromDb.get(
                            "lvl", ""), valuesFromDb.get("text", ""),
                        valuesFromDb.get("dated", "None"), valuesFromDb.get(
                            "datef", "None"),
                        valuesFromDb.get(
                            "scanner_ip", "None"), valuesFromDb.get("status", []), valuesFromDb.get("notes", ""), valuesFromDb.get("resultfile", ""), valuesFromDb.get("tags", []), valuesFromDb.get("infos", {}))

    def initialize(self, name, wave="", scope="", ip="", port="", proto="tcp", lvl="", text="",
                   dated="None", datef="None", scanner_ip="None", status=None, notes="", resultfile="", tags=None, infos=None):
        
        """Set values of tool
        Args:
            name: name of the tool (should match a command name)
            wave: the target wave name of this tool (only if lvl is "wave"). Default  ""
            scope: the scope string of the target scope of this tool (only if lvl is "network"). Default  ""
            ip: the target ip "ip" of this tool (only if lvl is "ip" or "port"). Default  ""
            port: the target port "port number" of this tool (only if lvl is "port"). Default  ""
            proto: the target port "proto" of this tool (only if lvl is "port"). Default  "tcp"
            lvl: the tool level of exploitation (wave, network, ip ort port/). Default ""
            text: the command to be launched. Can be empty if name is matching  a command. Default ""
            dated: a starting date and tiem for this interval in format : '%d/%m/%Y %H:%M:%S'. or the string "None"
            datef: an ending date and tiem for this interval in format : '%d/%m/%Y %H:%M:%S'. or the string "None"
            scanner_ip: the worker name that performed this tool. "None" if not performed yet. Default is "None"
            status: a list of status string describing this tool state. Default is None. (Accepted values for string in list are done, running, OOT, OOS)
            notes: notes concerning this tool (opt). Default to ""
            resultfile: an output file generated by the tool. Default is ""
            tags: a list of tags
            infos: a dictionnary of additional info
        Returns:
            this object
        """
        self.name = name
        self.wave = wave
        self.scope = scope
        self.ip = ip
        self.port = str(port)
        self.proto = proto
        self.lvl = lvl
        self.text = text
        self.dated = dated
        self.datef = datef
        self.scanner_ip = scanner_ip
        self.notes = notes
        self.resultfile = resultfile
        self.tags = tags if tags is not None else []
        self.infos = infos if infos is not None else {}
        if status is None:
            status = []
        elif isinstance(status, str):
            status = [status]
        self.status = status
        return self

    def delete(self):
        """
        Delete the tool represented by this model in database.
        """
        mongoInstance = MongoCalendar.getInstance()
        mongoInstance.delete("tools", {"_id": self._id})

    def addInDb(self):
        """
        Add this tool in database.

        Returns: a tuple with :
                * bool for success
                * mongo ObjectId : already existing object if duplicate, create object id otherwise 
        """
        base = self.getDbKey()
        mongoInstance = MongoCalendar.getInstance()
        # Checking unicity
        existing = mongoInstance.find("tools", base, False)
        if existing is not None:
            return False, existing["_id"]
        # Those are added to base after tool's unicity verification
        parent = self.getParent()
        base["scanner_ip"] = self.scanner_ip
        base["dated"] = self.dated
        base["datef"] = self.datef
        if isinstance(self.status, str):
            self.status = [self.status]
        base["parent"] = parent
        base["status"] = self.status
        base["tags"] = self.tags
        base["text"] = self.text
        base["resultfile"] = self.resultfile
        base["notes"] = self.notes
        res = mongoInstance.insert("tools", base, parent)
        self._id = res.inserted_id
        return True, res.inserted_id

    def setOutOfTime(self):
        """Set this tool as out of time (not matching any interval in wave)
        Add "OOT" in status
        """
        if "OOT" not in self.status:
            self.status.append("OOT")
            self.update({"status": self.status})

    def setInTime(self):
        """Set this tool as in time (matching any interval in wave)
        Remove "OOT" from status
        """
        if "OOT" in self.status:
            self.status.remove("OOT")
            self.update({"status": self.status})

    def setInScope(self):
        """Set this tool as out of scope (not matching any scope in wave)
        Add "OOS" in status
        """
        if "OOS" in self.status:
            self.status.remove("OOS")
            self.update()

    def setOutOfScope(self):
        """Set this tool as in scope (is matching at least one scope in wave)
        Remove "OOS" from status
        """
        if not "OOS" in self.status:
            self.status.append("OOS")
            self.update({"status": self.status})

    def setStatus(self,status):
        """Set this tool status with given list of status
        Args:
            list of string with status inside (accepted values are OOS, OOT, running, done)
        """
        self.status = status
        self.update({"status": self.status})

    def getStatus(self):
        """
        Get the tool executing status.

        Return:
            Returns a list of status status are :
                OOT : Out of time = This tool is in a wave which does not have any interval for now.
                OOS : Out os scope = This tool is in an IP OOS
                done : This tool is completed
                running : This tool is being run."""
        return self.status

    def getCommand(self):
        """
        Get the tool associated command.

        Return:
            Returns the Mongo dict command fetched instance associated with this tool's name.
        """
        mongoInstance = MongoCalendar.getInstance()
        commandTemplate = mongoInstance.findInDb(mongoInstance.calendarName,
                                                 "commands", {"name": self.name}, False)
        return commandTemplate

    @classmethod
    def __sanitize(cls, var_to_path):
        """Replace unwanted chars in variable given: '/', ' ' and ':' are changed to '_'
        Args:
            var_to_path: a string to sanitize to use a path folder
        Returns:
            modified arg as string
        """
        var_to_path = var_to_path.replace("/", "_")
        var_to_path = var_to_path.replace(" ", "_")
        var_to_path = var_to_path.replace(":", "_")
        return var_to_path

    def getOutputDir(self, calendarName):
        """
        Get the tool required output directory path.
        Args:
            calendarName: the pentest database name
        Return:
            Returns the output directory of this tool instance.
        """
        # get command needed directory
        output_dir = Tool.__sanitize(
            calendarName)+"/"+Tool.__sanitize(self.name)+"/"
        if self.wave != "" and self.wave is not None:
            output_dir += Tool.__sanitize(self.wave)+"/"
        if self.scope != "" and self.scope is not None:
            output_dir += Tool.__sanitize(self.scope)+"/"
        if self.ip != "" and self.ip is not None:
            output_dir += Tool.__sanitize(self.ip)+"/"
        if self.port != "" and self.port is not None:
            port_dir = str(self.port) if str(self.proto) == "tcp" else str(
                self.proto)+"/"+str(self.port)
            output_dir += Tool.__sanitize(port_dir)+"/"
        return output_dir

    def getCommandToExecute(self, outputDirectory):
        """
        Get the tool bash command to execute.
        Replace the command's text's variables with tool's informations.
        Args:
            outputDirectory: the output directory for this tool (see getOutputDir)
        Return:
            Returns the bash command of this tool instance.
        """
        toolHasCommand = self.text
        if toolHasCommand is not None and toolHasCommand.strip() != "":
            command = self.text
            lvl = self.lvl
        else:
            comm = self.getCommand()
            command = comm["text"]
            lvl = comm["lvl"]
        mongoInstance = MongoCalendar.getInstance()
        command = command.replace("|outputDir|", outputDirectory)
        command = command.replace("|wave|", self.wave)
        if lvl == "network" or lvl == "domain":
            command = command.replace("|scope|", self.scope)
            if Utils.isNetworkIp(self.scope) == False:
                depths = self.scope.split(".")
                if len(depths) > 2:
                    topdomain = ".".join(depths[1:])
                else:
                    topdomain = ".".join(depths)
                command = command.replace("|parent_domain|", topdomain)
        if lvl == "ip":
            command = command.replace("|ip|", self.ip)
            ip_db = mongoInstance.find("ips", {"ip":self.ip}, False)
            ip_infos = ip_db.get("infos", {})
            for info in ip_infos:
                command = command.replace("|ip.infos."+str(info)+"|", command)
        if lvl == "port":
            command = command.replace("|ip|", self.ip)
            command = command.replace("|port|", self.port)
            command = command.replace("|port.proto|", self.proto)
            port_db = mongoInstance.find("ports", {"port":self.port, "proto":self.proto, "ip":self.ip}, False)
            command = command.replace("|port.service|", port_db["service"])
            command = command.replace("|port.product|", port_db["product"])
            port_infos = port_db.get("infos", {})
            for info in port_infos:
                print("replacing "+"|port.infos."+str(info)+"|"+ "by "+str(info))
                command = command.replace("|port.infos."+str(info)+"|", str(port_infos[info]))
        return command

    def update(self, pipeline_set=None):
        """Update this object in database.
        Args:
            pipeline_set: (Opt.) A dictionnary with custom values. If None (default) use model attributes.
        """
        mongoInstance = MongoCalendar.getInstance()
        if pipeline_set is None:
            mongoInstance.update("tools", {"_id": ObjectId(self._id)}, {
                "$set": {"scanner_ip": str(self.scanner_ip), "dated": str(self.dated), "status": self.status,
                         "datef":  str(self.datef), "notes":  self.notes, "resultfile": self.resultfile, "tags": self.tags}})
        else:
            mongoInstance.update(
                "tools", {"_id": ObjectId(self._id)}, {"$set": pipeline_set})

    def _getParent(self):
        """
        Return the mongo ObjectId _id of the first parent of this object. For a Tool it is either a scope, an ip or a port depending on the tool's level.

        Returns:
            Returns the parent's ObjectId _id". or None if a type error occurs
        """
        mongoInstance = MongoCalendar.getInstance()
        try:
            if self.lvl == "wave":
                wave = mongoInstance.find("waves", {"wave": self.wave}, False)
                return wave["_id"]
            elif self.lvl == "network" or self.lvl == "domain":
                return mongoInstance.find("scopes", {"wave": self.wave, "scope": self.scope}, False)["_id"]
            elif self.lvl == "ip":
                return mongoInstance.find("ips", {"ip": self.ip}, False)["_id"]
            else:
                return mongoInstance.find("ports", {"ip": self.ip, "port": self.port, "proto": self.proto}, False)["_id"]
        except TypeError:
            # None type returned:
            return None

    def __str__(self):
        """
        Get a string representation of a tool.

        Returns:
            Returns the tool name. The wave name is prepended if tool lvl is "port" or "ip"
        """
        ret = self.name
        if self.lvl == "ip" or self.lvl == "port":
            ret = self.wave+"-"+ret
        return ret

    def getDetailedString(self):
        """
        Get a more detailed string representation of a tool.

        Returns:
            string
        """
        if self.lvl == "network" or self.lvl == "domain":
            return str(self.scope)+" "+str(self)
        elif self.lvl == "ip":
            return str(self.ip)+" "+str(self)
        else:
            return str(self.ip)+":"+str(self.proto+"/"+self.port)+" "+str(self)

    def getResultFile(self):
        """Returns the result file of this tool
        Returns:
            strings
        """
        return self.resultfile

    def markAsDone(self, file_name=None):
        """Set this tool status as done but keeps OOT or OOS.
        Args:
            file_name: the resulting file of thsi tool execution. Default is None
        """
        self.datef = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        newStatus = ["done"]
        if "OOS" in self.status:
            newStatus.append("OOS")
        if "OOT" in self.status:
            newStatus.append("OOT")
        self.status = newStatus
        self.resultfile = file_name
        self.update()

    def markAsRunning(self, workerName):
        """Set this tool status as running but keeps OOT or OOS.
        Sets the starting date to current time and ending date to "None"
        Args:
            workerName: the worker name that is running this tool
        """
        self.dated = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.datef = "None"
        newStatus = ["running"]
        if "OOS" in self.status:
            newStatus.append("OOS")
        if "OOT" in self.status:
            newStatus.append("OOT")
        self.status = newStatus
        self.scanner_ip = workerName
        self.update()

    def markAsNotDone(self):
        """Set this tool status as not done by removing "done" or "running" status.
        Also resets starting and ending date as well as worker name
        """
        self.dated = "None"
        self.datef = "None"
        self.scanner_ip = "None"
        if "done" in self.status:
            self.status.remove("done")
        if "running" in self.status:
            self.status.remove("running")
        self.update()

    def markAsError(self):
        """Set this tool status as not done by removing "done" or "running" and adding an error status.
        Also resets starting and ending date as well as worker name
        """
        self.dated = "None"
        self.datef = "None"
        self.scanner_ip = "None"
        if "done" in self.status:
            self.status.remove("done")
        if "running" in self.status:
            self.status.remove("running")
        self.status.append("error")
        self.update()

    def getDbKey(self):
        """Return a dict from model to use as unique composed key.
        Returns:
            A dict (7 keys :"wave", "scope", "ip", "port", "proto", "name", "lvl")
        """
        base = {"wave": self.wave, "scope": "", "ip": "", "port": "",
                "proto": "", "name": self.name, "lvl": self.lvl}
        if self.lvl == "wave":
            return base
        if self.lvl in ("domain", "network"):
            base["scope"] = self.scope
            return base
        base["ip"] = self.ip
        if self.lvl == "ip":
            return base
        base["port"] = self.port
        base["proto"] = self.proto
        return base
