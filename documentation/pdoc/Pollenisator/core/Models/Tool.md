Module Pollenisator.core.Models.Tool
====================================
Tool Model. A tool is an instanciation of a command against a target

Classes
-------

`Tool(valuesFromDb=None)`
:   Represents a Tool object that defines a tool. A tool is a command run materialized on a runnable object (wave, scope, ip, or port)
    
    Attributes:
        coll_name: collection name in pollenisator database
    
    Constructor
    Args:
        valueFromDb: a dict holding values to load into the object. A mongo fetched interval is optimal.
                    possible keys with default values are : _id(None), parent(None), tags([]), infos({}),
                    name(""), wave(""), scope(""), ip(""), port(""), proto("tcp"), lvl(""), text(""), dated("None"),
                    datef("None"), scanner_ip("None"), status([]), notes(""), resultfile("")

    ### Ancestors (in MRO)

    * core.Models.Element.Element

    ### Class variables

    `coll_name`
    :

    ### Methods

    `addInDb(self)`
    :   Add this tool in database.
        
        Returns: a tuple with :
                * bool for success
                * mongo ObjectId : already existing object if duplicate, create object id otherwise

    `delete(self)`
    :   Delete the tool represented by this model in database.

    `getCommand(self)`
    :   Get the tool associated command.
        
        Return:
            Returns the Mongo dict command fetched instance associated with this tool's name.

    `getCommandToExecute(self, outputDirectory)`
    :   Get the tool bash command to execute.
        Replace the command's text's variables with tool's informations.
        Args:
            outputDirectory: the output directory for this tool (see getOutputDir)
        Return:
            Returns the bash command of this tool instance.

    `getDbKey(self)`
    :   Return a dict from model to use as unique composed key.
        Returns:
            A dict (7 keys :"wave", "scope", "ip", "port", "proto", "name", "lvl")

    `getDetailedString(self)`
    :   Get a more detailed string representation of a tool.
        
        Returns:
            string

    `getOutputDir(self, calendarName)`
    :   Get the tool required output directory path.
        Args:
            calendarName: the pentest database name
        Return:
            Returns the output directory of this tool instance.

    `getResultFile(self)`
    :   Returns the result file of this tool
        Returns:
            strings

    `getStatus(self)`
    :   Get the tool executing status.
        
        Return:
            Returns a list of status status are :
                OOT : Out of time = This tool is in a wave which does not have any interval for now.
                OOS : Out os scope = This tool is in an IP OOS
                done : This tool is completed
                running : This tool is being run.

    `initialize(self, name, wave='', scope='', ip='', port='', proto='tcp', lvl='', text='', dated='None', datef='None', scanner_ip='None', status=None, notes='', resultfile='', tags=None, infos=None)`
    :   Set values of tool
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

    `markAsDone(self, file_name=None)`
    :   Set this tool status as done but keeps OOT or OOS.
        Args:
            file_name: the resulting file of thsi tool execution. Default is None

    `markAsNotDone(self)`
    :   Set this tool status as not done by removing "done" or "running" status.
        Also resets starting and ending date as well as worker name

    `markAsRunning(self, workerName)`
    :   Set this tool status as running but keeps OOT or OOS.
        Sets the starting date to current time and ending date to "None"
        Args:
            workerName: the worker name that is running this tool

    `setInScope(self)`
    :   Set this tool as out of scope (not matching any scope in wave)
        Add "OOS" in status

    `setInTime(self)`
    :   Set this tool as in time (matching any interval in wave)
        Remove "OOT" from status

    `setOutOfScope(self)`
    :   Set this tool as in scope (is matching at least one scope in wave)
        Remove "OOS" from status

    `setOutOfTime(self)`
    :   Set this tool as out of time (not matching any interval in wave)
        Add "OOT" in status

    `setStatus(self, status)`
    :   Set this tool status with given list of status
        Args:
            list of string with status inside (accepted values are OOS, OOT, running, done)

    `update(self, pipeline_set=None)`
    :   Update this object in database.
        Args:
            pipeline_set: (Opt.) A dictionnary with custom values. If None (default) use model attributes.