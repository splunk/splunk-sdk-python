apis = {
  "alerts/fired_alerts": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view fired alerts."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns a summary view of the list of all alerts that have been fired on the server.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to all alerts that have been fired on the server."
  }, 
  "alerts/fired_alerts/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete the fired alert."
          }, 
          "404": {
            "summary": "Fired alert does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes the record of this triggered alert.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view fired alert."
          }, 
          "404": {
            "summary": "Fired alert does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns a list of all unexpired triggered or fired instances of this alert.\n\nSpecify <code>-</code> for {name} to return all fired alerts. For example:\n\n<div class=\"samplecode\">\n<pre>\ncurl -k -u admin:pass https://localhost:8089/servicesNS/admin/search/alerts/fired_alerts/-\n</pre>\n</div>\n", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "apps/appinstall": {
    "methods": {
      "POST": {
        "config": "", 
        "params": {
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Specifies the app to install. Can be either a path to the app on a local disk or a URL to an app, such as the apps available from Splunkbase.", 
            "validation": ""
          }, 
          "update": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, installs an update to an app, overwriting the existing app folder.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to install app."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Installs a Splunk app from a local file or from a URL.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides for installation of apps from a URL or local file."
  }, 
  "apps/apptemplates": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view app templates."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists app templates that are used to create apps from the Mangager interface in Splunk Web.\n\nAn app template is valid as the \"template\" argument to POST to /services/apps/local. The app templates can be found by enumerating $SPLUNK_HOME/share/splunk/app_templates. Adding a new template takes effect without restarting splunkd or SplunkWeb.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to app templates that can be used to create new Splunk apps."
  }, 
  "apps/apptemplates/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view app template."
          }, 
          "404": {
            "summary": "app template does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Retrieves information about a specific app template.\n\nThis call is rarely used, as all the information is provided by the apps/templates endpoint, which does not require an explicit name.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "apps/local": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "refresh": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Scan for new apps and reload any objects those new apps contain.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view local apps."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information on all locally-installed apps.\n\nSplunkbase can correlate locally-installed apps with the same app on Splunkbase to notify users about app updates.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "author": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "For apps you intend to post to Splunkbase, enter the username of your splunk.com account.\n\nFor internal-use-only apps, include your full name and/or contact info (for example, email).", 
            "validation": ""
          }, 
          "configured": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates if the application's custom setup has been performed.\n'''Note''': This parameter is new with Splunk 4.2.4.", 
            "validation": ""
          }, 
          "description": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Short explanatory string displayed underneath the app's title in Launcher.\n\nTypically, short descriptions of 200 characters are more effective.", 
            "validation": ""
          }, 
          "label": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Defines the name of the app shown in the Splunk GUI and Launcher.\n\n* Must be between 5 and 80 characters.\n* Must not include \"Splunk For\" prefix.\n\nExamples of good labels:\n* IMAP\n* SQL Server Integration Services\n* FISMA Compliance", 
            "validation": ""
          }, 
          "manageable": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": " Indicates that the Splunk Manager can manage the app.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Name of the application to create. The name you select becomes the name of the folder on disk that contains the app.", 
            "validation": ""
          }, 
          "template": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (barebones &#124; sample_app)\n\nIndicates the app template to use when creating the app.\n\nSpecify either of the following:\n\n* barebones - contains basic framework for an app\n* sample_app - contains example views and searches\n\nYou can also specify any valid app template you may have previously added.", 
            "validation": ""
          }, 
          "visible": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": " Indicates if the app is visible and navigable from the UI.\n\nVisible apps require at least 1 view that is available from the UI", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create local app."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a new application.", 
        "urlParams": {}
      }
    }, 
    "summary": "Endpoint for creating new Splunk apps, and subsequently accessing, updating, and deleting local apps."
  }, 
  "apps/local/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete local app."
          }, 
          "404": {
            "summary": "Local app does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Removes the locally installed app with the name specified by {name}.\n\nAfter deleting an app, there might also be some manual cleanup. See \"Uninstall an app\" in the \"Meet Splunk Web and Splunk apps\" section of the Splunk Admin manual.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "params": {
          "refresh": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Reloads the objects contained in the locally installed app with the name specified by {name}.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view local app."
          }, 
          "404": {
            "summary": "Local app does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information about the locally installed app with the name specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "author": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "check_for_updates": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If set to true, Splunk checks Splunkbase for updates to this app.", 
            "validation": "validate(is_bool($check_for_updates$), \"Value of argument 'check_for_updates' must be a boolean\")"
          }, 
          "configured": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($configured$), \"Value of argument 'configured' must be a boolean\")"
          }, 
          "description": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "label": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "manageable": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "version": {
            "datatype": "version string", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies the version for the app. Each release of an app must change the version number.\n\nVersion numbers are a number followed by a sequence of numbers or dots. Pre-release versions can append a space and a single-word suffix like \"beta2\". Examples:\n\n* 1.2\n* 11.0.34\n* 2.0 beta\n* 1.3 beta2\n* 1.0 b2\n* 12.4 alpha\n* 11.0.34.234.254", 
            "validation": ""
          }, 
          "visible": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit local app."
          }, 
          "404": {
            "summary": "Local app does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the app specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "apps/local/{name}/package": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Package file for the app created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to create package for the app."
          }, 
          "404": {
            "summary": "App specified by {name} does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Archives the app specified by {name}, placing the archive in the following directory on your Splunk installation:\n\n:<code>$SPLUNK_HOME/etc/system/static/app-packages/{name}.spl</code>\n\nThe archive can then be downloaded from the management port of your Splunk installation:\n\n:<code>https://[Splunk Host]:[Management Port]/static/app-packages/{name}.spl</code>", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "apps/local/{name}/setup": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Set up information returned successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to setup app."
          }, 
          "404": {
            "summary": "App does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns set up information for the app specified by {name}. In the response to this operation, the actual setup script is listed under the key value, \"eai:setup.\" \n\nSome apps contain setup scripts that must be run before the app is enabled. For example, the [http://splunk-base.splunk.com/apps/22314/splunk-for-unix-and-linux Splunk for Unix and Linux app], available from [http://splunk-base.splunk.com/ Splunkbase], contains a setup script. \n\nFor more information on setup scripts, see [[Documentation:Splunk:Developer:SetupApp|Configure a setup screen]] in the [[Documentation:Splunk:Developer:Whatsinthismanual|Splunk Developer manual]].", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "apps/local/{name}/update": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Update information for the app was returned successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to update app."
          }, 
          "404": {
            "summary": "App does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns any update information available for the app specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "auth/login": {
    "methods": {
      "POST": {
        "params": {
          "password": {
            "datatype": "String", 
            "default": "", 
            "required": "True", 
            "summary": "The password for the user specified with <code>username</code>.", 
            "validation": ""
          }, 
          "username": {
            "datatype": "String", 
            "default": "", 
            "required": "True", 
            "summary": "The Splunk account username.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Authenticated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }
        }, 
        "summary": "Returns a session key to be used when making REST calls to splunkd.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides user authentication. \n\n<b>Note:</b> This endpoint is under 'auth' and not 'authentication' for backwards compatibility."
  }, 
  "authentication/auth-tokens": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view auth-tokens."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Does nothing.  Is a placeholder for potential future information.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "This is a special key, always being \"_create\"", 
            "validation": ""
          }, 
          "nonce": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "An alphanumeric string representing a unique identifier for this request", 
            "validation": ""
          }, 
          "peername": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The name of the splunk server requesting this token", 
            "validation": ""
          }, 
          "sig": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "A cryptographic signature of the \"userid\", \"username\", \"nonce\", and \"ts\" arguments", 
            "validation": ""
          }, 
          "ts": {
            "datatype": "Number", 
            "default": "", 
            "required": "true", 
            "summary": "The unix time at which the signature was created", 
            "validation": ""
          }, 
          "userid": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the user requesting this token", 
            "validation": ""
          }, 
          "username": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the user requesting this token", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create auth-tokens."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates an authentication token", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for creation of authentication tokens"
  }, 
  "authentication/current-context": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view current-context."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists one item named \"context\" which contains the name of the current user", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for displaying the current user context"
  }, 
  "authentication/current-context/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view current-context."
          }, 
          "404": {
            "summary": "current-context does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Displays an item (always named \"context\") that contains the name of the current user.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "authentication/httpauth-tokens": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view httpauth-tokens."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List all currently active session tokens", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for management of session tokens"
  }, 
  "authentication/httpauth-tokens/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete httpauth-token."
          }, 
          "404": {
            "summary": "httpauth-token does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "End the session associated with this token", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view httpauth-tokens."
          }, 
          "404": {
            "summary": "httpauth-token does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Get information about a specific session token", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "authentication/users": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view users."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns a list of all the users registered on the server.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "createrole": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The name of a role to create for the user. After creating the role, you can later edit that role to specify what access that user has to Splunk.", 
            "validation": ""
          }, 
          "defaultApp": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a default app for the user.\n\nThe default app specified here overrides the default app inherited from the user's roles.", 
            "validation": ""
          }, 
          "email": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify an email address for the user.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The Splunk username for the user to login to splunk.\n\nusernames must be unique on the system.", 
            "validation": ""
          }, 
          "password": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The user's password.", 
            "validation": ""
          }, 
          "realname": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A full name to associate with the user.", 
            "validation": ""
          }, 
          "restart_background_jobs": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether to restart background search jobs when Splunk restarts.\n\nIf true, a background search job for this user that has not completed is restarted when Splunk restarts.", 
            "validation": ""
          }, 
          "roles": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A role to assign to this user. To assign multiple roles, send them in separate <code>roles</code> parameters.\n\nWhen creating a user, at least one role is required. Either specify one or more roles with this parameter or create a role using the <code>createrole</code> parameter.", 
            "validation": ""
          }, 
          "tz": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Timezone to use when displaying dates for this user.\n'''Note''': This parameter is new with Splunk 4.3.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create user."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a new user.\n\nWhen creating a user you must specify at least one role. You can specify one or more roles with the <code>roles</code> parameter, or you can use the <code>createrole</code> parameter to create a role for the user.\n\nRefer to [[Documentation:Splunk:Admin:Aboutusersandroles|About users and roles]] in the [[Documentation:Splunk:Admin:Whatsinthismanual|Splunk Admin manual]] for details about Splunk users, roles, and capabilities. ", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to Splunk users.\n\nRefer to [[Documentation:Splunk:Admin:Aboutusersandroles|About users and roles]] in the [[Documentation:Splunk:Admin:Whatsinthismanual|Splunk Admin manual]] for details about Splunk users, roles, and capabilities. "
  }, 
  "authentication/users/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete user."
          }, 
          "404": {
            "summary": "User does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Removes the user from the system.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view user."
          }, 
          "404": {
            "summary": "User does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information about the user.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "defaultApp": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "email": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "password": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "realname": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "restart_background_jobs": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "roles": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "tz": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit user."
          }, 
          "404": {
            "summary": "User does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Update information about the user specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "authorization/capabilities": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view capabilities."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List all system capabiilities.\n\nRefer to the [[Documentation:Splunk:Admin:Addandeditroles#List_of_available_capabilities|List of available capabilities]] in the [[Documentation:Splunk:Admin:Whatsinthismanual|Splunk Admin manual]] for details.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to Splunk's capability authorization system.\n\nRefer to [[Documentation:Splunk:Admin:Aboutusersandroles|About users and roles]] in the [[Documentation:Splunk:Admin:Whatsinthismanual|Splunk Admin manual]] for details about Splunk users, roles, and capabilities."
  }, 
  "authorization/capabilities/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view capabilities."
          }, 
          "404": {
            "summary": "Capability does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List a particular system capability name. This does not list any further information besides the name.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "authorization/roles": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view roles."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists all roles and the permissions for each role. Refer to [[Documentation:Splunk:Admin:Aboutusersandroles|About users and roles]] in the [[Documentation:Splunk:Admin:Whatsinthismanual|Splunk Admin manual]] for details about Splunk users, roles, and capabilities. ", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "capabilities": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A capability to assign to this role. To send multiple capabilities, send this argument multiple times.\n\nRoles inherit all capabilities from imported roles\n\nCapabilities available are:\n\n* admin_all_objects\n* change_authentication\n* change_own_password\n* delete_by_keyword\n* edit_deployment_client\n* edit _depoyment_server\n* edit_dist_peer\n* edit_forwarders\n* edit_httpauths\n* edit_input_defaults\n* edit_monitor\n* edit_scripted\n* edit_search_server\n* edit_splunktcp\n* edit_splunktcp_ssl\n* edit_tcp\n* edit_udp\n* edit_web_settings\n* get_metadata\n* get_typeahead\n* indexes_edit\n* license_edit\n* license_tab\n* list_deployment_client\n* list_forwarders\n* list_httpauths\n* list_inputs\n* request_remote_tok\n* rest_apps_management\n* rest_apps_view\n* rest_properties_get\n* rest_properties_set\n* restart_splunkd\n* rtsearch\n* schedule_search\n* search\n* use_file_operator", 
            "validation": ""
          }, 
          "defaultApp": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify the name of the app to use as the default app for the role.A user-specific default app will override this.\n\nThe name you specify is the name of the folder containing the app.", 
            "validation": ""
          }, 
          "imported_roles": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a role to import attributes from. Specify many of these separately to import multiple roles. By default a role imports no other roles.\n\nImporting other roles imports all aspects of that role, such as capabilities and allowed indexes to search. In combining multiple roles, the effective value for each attribute is value with the broadest permissions.\n\nDefault Splunk roles are:\n\n* admin\n* can_delete\n* power\n* user\n\nYou can specify additional roles that have been created.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the user role to create.", 
            "validation": ""
          }, 
          "rtSrchJobsQuota": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Specify the maximum number of concurrent real time search jobs for this role.\n\nThis count is independent from the normal search jobs limit.", 
            "validation": ""
          }, 
          "srchDiskQuota": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies the maximum disk space in MB that can be used by a user's search jobs. For example, 100 limits this role to 100 MB total.", 
            "validation": ""
          }, 
          "srchFilter": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a search string that restricts the scope of searches run by this role. Search results for this role only show events that also match the search string you specify.   In the case that a user has multiple roles with different search filters, they are combined with an OR.\n\nThe search string can include source, host, index, eventtype, sourcetype, search fields, *, OR and, AND. \n\nExample: \"host=web* OR source=/var/log/*\"\n\nNote: You can also use the srchIndexesAllowed and srchIndexesDefault parameters to limit the search on indexes.", 
            "validation": ""
          }, 
          "srchIndexesAllowed": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "An index this role has permissions to search. To set several of these, pass this argument several times. These may be wildcarded, but the index name must begin with an underscore to match internal indexes.\n\nSearch indexes available by default from Splunk include:\n\n* All internal indexes\n* All non-internal indexes\n* _audit\n* _blocksignature\n* _internal\n* _thefishbucket\n* history\n* main\n\nYou can also specify other search indexes that have been added to the server.", 
            "validation": ""
          }, 
          "srchIndexesDefault": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A search index that searches for this role default to when no index is specified. To set several of these, pass this argument multiple times. These may be wildcarded, but the index name must begin with an underscore to match internal indexes.\n\nA user with this role can search other indexes using \"index= \" \n\nFor example, \"index=special_index\".\n\nSearch indexes available by default from Splunk include:\n\n* All internal indexes\n* All non-internal indexes\n* _audit\n* _blocksignature\n* _internal\n* _thefishbucket\n* history\n* main\n* other search indexes that have been added to the server\n\nThese indexes can be wildcarded, with the exception that '*' does not match internal indexes. To match internal indexes, start with '_'. All internal indexes are represented by '_*'.", 
            "validation": ""
          }, 
          "srchJobsQuota": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "The maximum number of concurrent searches a user with this role is allowed to run. In the event of many roles per user, the maximum of these quotas is applied.", 
            "validation": ""
          }, 
          "srchTimeWin": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Maximum time span of a search, in seconds.\n \nBy default, searches are not limited to any specific time window. To override any search time windows from imported roles, set srchTimeWin to '0', as the 'admin' role does.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create role."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a user role. Refer to [[Documentation:Splunk:Admin:Aboutusersandroles|About users and roles]] in the [[Documentation:Splunk:Admin:Whatsinthismanual|Splunk Admin manual]] for details about Splunk users, roles, and capabilities.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to Splunk user roles.\n\nRefer to [[Documentation:Splunk:Admin:Aboutusersandroles|About users and roles]] in the [[Documentation:Splunk:Admin:Whatsinthismanual|Splunk Admin manual]] for details about Splunk users, roles, and capabilities. "
  }, 
  "authorization/roles/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete role."
          }, 
          "404": {
            "summary": "Role does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes the role specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view role."
          }, 
          "404": {
            "summary": "Role does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists the permissions for the role specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "capabilities": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "defaultApp": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "imported_roles": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "rtSrchJobsQuota": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "srchDiskQuota": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "srchFilter": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "srchIndexesAllowed": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "srchIndexesDefault": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "srchJobsQuota": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "srchTimeWin": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit role."
          }, 
          "404": {
            "summary": "Role does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the role specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "configs/conf-{file}": {
    "methods": {
      "GET": {
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Maximum number of items to return.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Boolean predicate to filter results.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Direction to sort by (asc/desc).", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to sort by.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Collating sequence for the sort (auto, alpha, alpha_case, num).", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view configuration file."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists all stanzas contained in the named configuration file.", 
        "urlParams": {
          "file": {
            "required": "true", 
            "summary": "file"
          }
        }
      }, 
      "POST": {
        "params": {
          "&lt;key&gt;": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "This operation accepts an arbitrary set of key/value pairs to populate in the created stanza.  (There is no actual parameter named \"key\".)", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the stanza to create.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to create configuration stanza."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Allows for creating the stanza specified by \"name\" in the configuration file specified by {file}.", 
        "urlParams": {
          "file": {
            "required": "true", 
            "summary": "file"
          }
        }
      }
    }, 
    "summary": "Provides raw access to Splunk's \".conf\" configuration files.\n\nRefer to [[Documentation:Splunk:RESTAPI:RESTconfigurations|Accessing and updating Splunk configurations]] for a comparison of these endpoints with the <code>properties/</code> endpoints."
  }, 
  "configs/conf-{file}/{name}": {
    "methods": {
      "DELETE": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete configuration stanza."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes the named stanza in the named configuration file.", 
        "urlParams": {
          "file": {
            "required": "true", 
            "summary": "file"
          }, 
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view configuration stanza."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Display only the named stanza from the named configuration file.", 
        "urlParams": {
          "file": {
            "required": "true", 
            "summary": "file"
          }, 
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "params": {
          "&lt;key&gt;": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "This operation accepts an arbitrary set of key/value pairs to populate in the created stanza.  (There is no actual parameter named \"key\".)", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit configuration stanza."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Allows for editing the named stanza from the named configuration file.", 
        "urlParams": {
          "file": {
            "required": "true", 
            "summary": "file"
          }, 
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/commands": {
    "methods": {
      "GET": {
        "config": "commands", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view commands."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List all python search commands.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to Python search commands used in Splunk."
  }, 
  "data/commands/{name}": {
    "methods": {
      "GET": {
        "config": "commands", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view command."
          }, 
          "404": {
            "summary": "Command does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Provide information about a specific python search command.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/indexes": {
    "methods": {
      "GET": {
        "config": "indexes", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }, 
          "summarize": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "If true, leaves out certain index details in order to provide a faster response.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "OK"
          }, 
          "400": {
            "summary": "TO DO: provide the rest of the status codes"
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view indexes."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists the recognized indexes on the server.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "indexes", 
        "params": {
          "assureUTF8": {
            "datatype": "Boolean", 
            "default": "false", 
            "required": "false", 
            "summary": "Verifies that all data retreived from the index is proper UTF8.\n\nWill degrade indexing performance when enabled (set to true).\n\nCan only be set globally", 
            "validation": ""
          }, 
          "blockSignSize": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Controls how many events make up a block for block signatures.\n\nIf this is set to 0, block signing is disabled for this index.\n\nA recommended value is 100.", 
            "validation": "validate(isint(blockSignSize) AND blockSignSize >= 0,\"blockSignSize must be a non-negative integer\")"
          }, 
          "coldPath": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "An absolute path that contains the colddbs for the index. The path must be readable and writable. Cold databases are opened as needed when searching. May be defined in terms of a volume definition (see volume section below).\n\nRequired. Splunk will not start if an index lacks a valid coldPath.", 
            "validation": ""
          }, 
          "coldToFrozenDir": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Destination path for the frozen archive. Use as an alternative to a coldToFrozenScript. Splunk automatically puts frozen buckets in this directory.\n\nBucket freezing policy is as follows:\n* New style buckets (4.2 and on): removes all files but the rawdata\n:To thaw, run <code>splunk rebuild <bucket dir></code> on the bucket, then move to the thawed directory\n* Old style buckets (Pre-4.2): gzip all the .data and .tsidx files\n:To thaw, gunzip the zipped files and move the bucket into the thawed directory\n\nIf both coldToFrozenDir and coldToFrozenScript are specified, coldToFrozenDir takes precedence", 
            "validation": ""
          }, 
          "coldToFrozenScript": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Path to the archiving script.\n\nIf your script requires a program to run it (for example, python), specify the program followed by the path. The script must be in $SPLUNK_HOME/bin or one of its subdirectories.\n\nSplunk ships with an example archiving script in $SPLUNK_HOME/bin called coldToFrozenExample.py. Splunk DOES NOT recommend using this example script directly. It uses a default path, and if modified in place any changes will be overwritten on upgrade.\n\nSplunk recommends copying the example script to a new file in bin and modifying it for your system.  Most importantly, change the default archive path to an existing directory that fits your needs.\n\nIf your new script in bin/ is named myColdToFrozen.py, set this key to the following:\n\n<code>coldToFrozenScript = \"$SPLUNK_HOME/bin/python\" \"$SPLUNK_HOME/bin/myColdToFrozen.py\"</code>\n\nBy default, the example script has two possible behaviors when archiving:\n* For buckets created from version 4.2 and on, it removes all files except for rawdata. To thaw: cd to the frozen bucket and type <code>splunk rebuild .</code>, then copy the bucket to thawed for that index.  We recommend using the coldToFrozenDir parameter unless you need to perform a more advanced operation upon freezing buckets.\n* For older-style buckets, we simply gzip all the .tsidx files. To thaw: cd to the frozen bucket and unzip the tsidx files, then copy the bucket to thawed for that index", 
            "validation": ""
          }, 
          "compressRawdata": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "This parameter is ignored. The splunkd process always compresses raw data.", 
            "validation": ""
          }, 
          "enableOnlineBucketRepair": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "Enables asynchronous \"online fsck\" bucket repair, which runs concurrently with Splunk.\n\nWhen enabled, you do not have to wait until buckets are repaired to start Splunk. However, you might observe a slight performance degratation.\n\n'''Note:''' This endpoint is new in Splunk 4.3.", 
            "validation": ""
          }, 
          "frozenTimePeriodInSecs": {
            "datatype": "Number", 
            "default": "188697600", 
            "required": "false", 
            "summary": "Number of seconds after which indexed data rolls to frozen.  Defaults to 188697600 (6 years).\n\nFreezing data means it is removed from the index.  If you need to archive your data, refer to coldToFrozenDir and coldToFrozenScript parameter documentation.", 
            "validation": "validate(isint(frozenTimePeriodInSecs) AND frozenTimePeriodInSecs >= 0,\"frozenTimePeriodInSecs must be a non-negative integer\")"
          }, 
          "homePath": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "An absolute path that contains the hot and warm buckets for the index.\n\nRequired. Splunk will not start if an index lacks a valid homePath.\n\nCAUTION: Path MUST be readable and writable.", 
            "validation": ""
          }, 
          "maxBloomBackfillBucketAge": {
            "datatype": "Number", 
            "default": "30d", 
            "required": "false", 
            "summary": "Valid values are: Integer[m|s|h|d]\n\nIf a warm or cold bucket is older than the specified age, do not create or rebuild its bloomfilter. Specify 0 to never rebuild bloomfilters.\n\nFor example, if a bucket is older than specified with maxBloomBackfillBucketAge, and the rebuilding of its bloomfilter started but did not finish, do not rebuild it.", 
            "validation": ""
          }, 
          "maxConcurrentOptimizes": {
            "datatype": "Number", 
            "default": "3", 
            "required": "false", 
            "summary": "The number of concurrent optimize processes that can run against a hot bucket.\n\nThis number should be increased if instructed by Splunk Support.  Typically the default value should suffice.\n", 
            "validation": "validate(isint(maxConcurrentOptimizes) AND maxConcurrentOptimizes >= 0,\"maxConcurrentOptimizes must be a non-negative integer\")"
          }, 
          "maxDataSize": {
            "datatype": "Number", 
            "default": "auto", 
            "required": "false", 
            "summary": "The maximum size in MB for a hot DB to reach before a roll to warm is triggered. Specifying \"auto\" or \"auto_high_volume\" causes Splunk to autotune this parameter (recommended).Use \"auto_high_volume\" for high volume indexes (such as the main index); otherwise, use \"auto\".  A \"high volume index\" would typically be considered one that gets over 10GB of data per day.\n* \"auto\" sets the size to 750MB.\n* \"auto_high_volume\" sets the size to 10GB on 64-bit, and 1GB on 32-bit systems.\n\nAlthough the maximum value you can set this is 1048576 MB, which corresponds to 1 TB, a reasonable number ranges anywhere from 100 - 50000. Any number outside this range should be approved by Splunk Support before proceeding.\n\nIf you specify an invalid number or string, maxDataSize will be auto tuned.\n\nNOTE: The precise size of your warm buckets may vary from maxDataSize, due to post-processing and timing issues with the rolling policy.", 
            "validation": "validate(maxDataSize == \"auto\" OR maxDataSize == \"auto_high_volume\" OR isint(maxDataSize) AND maxDataSize >= 0,\"maxDataSize must be one of auto, auto_high_volume or non-negative integer\")"
          }, 
          "maxHotBuckets": {
            "datatype": "Number", 
            "default": "3", 
            "required": "false", 
            "summary": "Maximum hot buckets that can exist per index. Defaults to 3.\n\nWhen maxHotBuckets is exceeded, Splunk rolls the least recently used (LRU) hot bucket to warm. Both normal hot buckets and quarantined hot buckets count towards this total. This setting operates independently of maxHotIdleSecs, which can also cause hot buckets to roll.", 
            "validation": "validate(isint(maxHotBuckets) AND maxHotBuckets >= 0,\"maxHotBuckets must be a non-negative integer\")"
          }, 
          "maxHotIdleSecs": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "\"Maximum life, in seconds, of a hot bucket. Defaults to 0.\n\nIf a hot bucket exceeds maxHotIdleSecs, Splunk rolls it to warm. This setting operates independently of maxHotBuckets, which can also cause hot buckets to roll. A value of 0 turns off the idle check (equivalent to INFINITE idle time).", 
            "validation": "validate(isint(maxHotIdleSecs) AND maxHotIdleSecs >= 0,\"maxHotIdleSecs must be a non-negative integer\")"
          }, 
          "maxHotSpanSecs": {
            "datatype": "Number", 
            "default": "7776000", 
            "required": "false", 
            "summary": "Upper bound of target maximum timespan of hot/warm buckets in seconds. Defaults to 7776000 seconds (90 days).\n\nNOTE: f you set this too small, you can get an explosion of hot/warm buckets in the filesystem. The system sets a lower bound implicitly for this parameter at 3600, but this is an advanced parameter that should be set with care and understanding of the characteristics of your data.", 
            "validation": "validate(isint(maxHotSpanSecs) AND maxHotSpanSecs >= 0,\"maxHotSpanSecs must be a non-negative integer\")"
          }, 
          "maxMemMB": {
            "datatype": "Number", 
            "default": "5", 
            "required": "false", 
            "summary": "The amount of memory, expressed in MB, to allocate for buffering a single tsidx file into memory before flushing to disk.  Defaults to 5. The default is recommended for all environments.\n\nIMPORTANT:  Calculate this number carefully. Setting this number incorrectly may have adverse effects on your systems memory and/or splunkd stability/performance.", 
            "validation": "validate(isint(maxMemMB) AND maxMemMB >= 0,\"maxMemMB must be a non-negative integer\")"
          }, 
          "maxMetaEntries": {
            "datatype": "Number", 
            "default": "1000000", 
            "required": "false", 
            "summary": "Sets the maximum number of unique lines in .data files in a bucket, which may help to reduce memory consumption. If set to 0, this setting is ignored (it is treated as infinite).\n\nIf exceeded, a hot bucket is rolled to prevent further increase. If your buckets are rolling due to Strings.data hitting this limit, the culprit may be the <code>punct</code> field in your data.  If you don't use punct, it may be best to simply disable this (see props.conf.spec in $SPLUNK_HOME/etc/system/README).\n\nThere is a small time delta between when maximum is exceeded and bucket is rolled. This means a bucket may end up with epsilon more lines than specified, but this is not a major concern unless excess is significant.", 
            "validation": ""
          }, 
          "maxTotalDataSizeMB": {
            "datatype": "Number", 
            "default": "500000", 
            "required": "false", 
            "summary": "The maximum size of an index (in MB). If an index grows larger than the maximum size, the oldest data is frozen.", 
            "validation": "validate(isint(maxTotalDataSizeMB) AND maxTotalDataSizeMB >= 0,\"maxTotalDataSizeMB must be a non-negative integer\")"
          }, 
          "maxWarmDBCount": {
            "datatype": "Number", 
            "default": "300", 
            "required": "false", 
            "summary": "The maximum number of warm buckets. If this number is exceeded, the warm bucket/s with the lowest value for their latest times will be moved to cold.", 
            "validation": "validate(isint(maxWarmDBCount) AND maxWarmDBCount >= 0,\"maxWarmDBCount must be a non-negative integer\")"
          }, 
          "minRawFileSyncSecs": {
            "datatype": "Number", 
            "default": "disable", 
            "required": "false", 
            "summary": "Specify an integer (or \"disable\") for this parameter.\n\nThis parameter sets how frequently splunkd forces a filesystem sync while compressing journal slices.\n\nDuring this interval, uncompressed slices are left on disk even after they are compressed. Then splunkd forces a filesystem sync of the compressed journal and removes the accumulated uncompressed files.\n\nIf 0 is specified, splunkd forces a filesystem sync after every slice completes compressing. Specifying \"disable\" disables syncing entirely: uncompressed slices are removed as soon as compression is complete.\n\n<b>NOTE:</b> Some filesystems are very inefficient at performing sync operations, so only enable this if you are sure it is needed", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the index to create.", 
            "validation": ""
          }, 
          "partialServiceMetaPeriod": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Related to serviceMetaPeriod.  If set, it enables metadata sync every <integer> seconds, but only for records where the sync can be done efficiently in-place, without requiring a full re-write of the metadata file.  Records that require full re-write are be sync'ed at serviceMetaPeriod.\n\n<code>partialServiceMetaPeriod</code> specifies, in seconds, how frequently it should sync.  Zero means that this feature is turned off and serviceMetaPeriod is the only time when metadata sync happens.\n\nIf the value of partialServiceMetaPeriod is greater than serviceMetaPeriod, this setting has no effect.\n\nBy default it is turned off (zero).", 
            "validation": ""
          }, 
          "quarantineFutureSecs": {
            "datatype": "Number", 
            "default": "2592000", 
            "required": "false", 
            "summary": "Events with timestamp of <code>quarantineFutureSecs</code> newer than \"now\" are dropped into quarantine bucket. Defaults to 2592000 (30 days).\n\nThis is a mechanism to prevent main hot buckets from being polluted with fringe events.", 
            "validation": "validate(isint(quarantineFutureSecs) AND quarantineFutureSecs >= 0,\"quarantineFutureSecs must be a non-negative integer\")"
          }, 
          "quarantinePastSecs": {
            "datatype": "Number", 
            "default": "77760000", 
            "required": "false", 
            "summary": "Events with timestamp of <code>quarantinePastSecs</code> older than \"now\" are dropped into quarantine bucket. Defaults to 77760000 (900 days).\n\nThis is a mechanism to prevent the main hot buckets from being polluted with fringe events.", 
            "validation": "validate(isint(quarantinePastSecs) AND quarantinePastSecs >= 0,\"quarantinePastSecs must be a non-negative integer\")"
          }, 
          "rawChunkSizeBytes": {
            "datatype": "Number", 
            "default": "131072", 
            "required": "false", 
            "summary": "Target uncompressed size in bytes for individual raw slice in the rawdata journal of the index. Defaults to 131072 (128KB). 0 is not a valid value. If 0 is specified, <code>rawChunkSizeBytes</code> is set to the default value.\n\nNOTE: rawChunkSizeBytes only specifies a target chunk size. The actual chunk size may be slightly larger by an amount proportional to an individual event size.\n\nWARNING: This is an advanced parameter. Only change it if you are instructed to do so by Splunk Support.", 
            "validation": "validate(isint(rawChunkSizeBytes) AND rawChunkSizeBytes >= 0,\"rawChunkSizeBytes must be a non-negative integer\")"
          }, 
          "rotatePeriodInSecs": {
            "datatype": "Number", 
            "default": "60", 
            "required": "false", 
            "summary": "How frequently (in seconds) to check if a new hot bucket needs to be created. Also, how frequently to check if there are any warm/cold buckets that should be rolled/frozen.", 
            "validation": "validate(isint(rotatePeriodInSecs) AND rotatePeriodInSecs >= 0,\"rotatePeriodInSecs must be a non-negative integer\")"
          }, 
          "serviceMetaPeriod": {
            "datatype": "Number", 
            "default": "25", 
            "required": "false", 
            "summary": "Defines how frequently metadata is synced to disk, in seconds. Defaults to 25 (seconds).\n\nYou may want to set this to a higher value if the sum of your metadata file sizes is larger than many tens of megabytes, to avoid the hit on I/O in the indexing fast path.", 
            "validation": ""
          }, 
          "syncMeta": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "When <code>true</code>, a sync operation is called before file descriptor is closed on metadata file updates. This functionality improves integrity of metadata files, especially in regards to operating system crashes/machine failures.\n\n<b>Note</b>: Do not change this parameter without the input of a Splunk Support.", 
            "validation": ""
          }, 
          "thawedPath": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "An absolute path that contains the thawed (resurrected) databases for the index.\n\nCannot be defined in terms of a volume definition.\n\nRequired. Splunk will not start if an index lacks a valid <code>thawedPath</codePath>.\n\n", 
            "validation": ""
          }, 
          "throttleCheckPeriod": {
            "datatype": "Number", 
            "default": "15", 
            "required": "false", 
            "summary": "Defines how frequently Splunk checks for index throttling condition, in seconds. Defaults to 15 (seconds).\n\n<b>Note</b>: Do not change this parameter without the input of a Splunk Support.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Index created successfully; followed by header:\n\n<code>Location: /services/data/indexes/{name}</code>"
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create index."
          }, 
          "409": {
            "summary": "The index name already exists."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a new index with the given name.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides services to create and manage data indexes."
  }, 
  "data/indexes/{name}": {
    "methods": {
      "GET": {
        "config": "indexes", 
        "params": {
          "summarize": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "If true, leaves out certain index details in order to provide a faster response.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view index."
          }, 
          "404": {
            "summary": "Index does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Retrieves information about the named index.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "indexes", 
        "params": {
          "assureUTF8": {
            "datatype": "INHERITED", 
            "default": "false", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blockSignSize": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(blockSignSize) AND blockSignSize >= 0,\"blockSignSize must be a non-negative integer\")"
          }, 
          "coldToFrozenDir": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "coldToFrozenScript": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "compressRawdata": {
            "datatype": "INHERITED", 
            "default": "true", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "enableOnlineBucketRepair": {
            "datatype": "INHERITED", 
            "default": "true", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "frozenTimePeriodInSecs": {
            "datatype": "INHERITED", 
            "default": "188697600", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(frozenTimePeriodInSecs) AND frozenTimePeriodInSecs >= 0,\"frozenTimePeriodInSecs must be a non-negative integer\")"
          }, 
          "maxBloomBackfillBucketAge": {
            "datatype": "INHERITED", 
            "default": "30d", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "maxConcurrentOptimizes": {
            "datatype": "INHERITED", 
            "default": "3", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(maxConcurrentOptimizes) AND maxConcurrentOptimizes >= 0,\"maxConcurrentOptimizes must be a non-negative integer\")"
          }, 
          "maxDataSize": {
            "datatype": "INHERITED", 
            "default": "auto", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(maxDataSize == \"auto\" OR maxDataSize == \"auto_high_volume\" OR isint(maxDataSize) AND maxDataSize >= 0,\"maxDataSize must be one of auto, auto_high_volume or non-negative integer\")"
          }, 
          "maxHotBuckets": {
            "datatype": "INHERITED", 
            "default": "3", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(maxHotBuckets) AND maxHotBuckets >= 0,\"maxHotBuckets must be a non-negative integer\")"
          }, 
          "maxHotIdleSecs": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(maxHotIdleSecs) AND maxHotIdleSecs >= 0,\"maxHotIdleSecs must be a non-negative integer\")"
          }, 
          "maxHotSpanSecs": {
            "datatype": "INHERITED", 
            "default": "7776000", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(maxHotSpanSecs) AND maxHotSpanSecs >= 0,\"maxHotSpanSecs must be a non-negative integer\")"
          }, 
          "maxMemMB": {
            "datatype": "INHERITED", 
            "default": "5", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(maxMemMB) AND maxMemMB >= 0,\"maxMemMB must be a non-negative integer\")"
          }, 
          "maxMetaEntries": {
            "datatype": "INHERITED", 
            "default": "1000000", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "maxTotalDataSizeMB": {
            "datatype": "INHERITED", 
            "default": "500000", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(maxTotalDataSizeMB) AND maxTotalDataSizeMB >= 0,\"maxTotalDataSizeMB must be a non-negative integer\")"
          }, 
          "maxWarmDBCount": {
            "datatype": "INHERITED", 
            "default": "300", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(maxWarmDBCount) AND maxWarmDBCount >= 0,\"maxWarmDBCount must be a non-negative integer\")"
          }, 
          "minRawFileSyncSecs": {
            "datatype": "INHERITED", 
            "default": "disable", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "partialServiceMetaPeriod": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "quarantineFutureSecs": {
            "datatype": "INHERITED", 
            "default": "2592000", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(quarantineFutureSecs) AND quarantineFutureSecs >= 0,\"quarantineFutureSecs must be a non-negative integer\")"
          }, 
          "quarantinePastSecs": {
            "datatype": "INHERITED", 
            "default": "77760000", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(quarantinePastSecs) AND quarantinePastSecs >= 0,\"quarantinePastSecs must be a non-negative integer\")"
          }, 
          "rawChunkSizeBytes": {
            "datatype": "INHERITED", 
            "default": "131072", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(rawChunkSizeBytes) AND rawChunkSizeBytes >= 0,\"rawChunkSizeBytes must be a non-negative integer\")"
          }, 
          "rotatePeriodInSecs": {
            "datatype": "INHERITED", 
            "default": "60", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint(rotatePeriodInSecs) AND rotatePeriodInSecs >= 0,\"rotatePeriodInSecs must be a non-negative integer\")"
          }, 
          "serviceMetaPeriod": {
            "datatype": "INHERITED", 
            "default": "25", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "syncMeta": {
            "datatype": "INHERITED", 
            "default": "true", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "throttleCheckPeriod": {
            "datatype": "INHERITED", 
            "default": "15", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Properties for the index were updated successfully."
          }, 
          "400": {
            "summary": "Some arguments were invalid"
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit index."
          }, 
          "404": {
            "summary": "The specified index was not found."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Unspecified error"
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the data index specified by <code>{name}</code> with information specified with index attributes.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/ad": {
    "methods": {
      "GET": {
        "config": "admon", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Boolean predicate to filter results.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc | desc)\n\nIndicates whether to sort the entries returned in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to sort by.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto | alpha | alpha_case | num)\n\nIndicates the collating sequence for sorting the returned entries.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view AD monitoring configuration."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets current AD monitoring configuration.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "admon", 
        "params": {
          "disabled": {
            "datatype": "Boolean", 
            "default": "1", 
            "required": "false", 
            "summary": "Indicates whether the monitoring is disabled.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The index in which to store the gathered data.", 
            "validation": ""
          }, 
          "monitorSubtree": {
            "datatype": "Number", 
            "default": "1", 
            "required": "true", 
            "summary": "Whether or not to monitor the subtree(s) of a given directory tree path.  1 means yes, 0 means no.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "A unique name that represents a configuration or set of configurations for a specific domain controller (DC).", 
            "validation": ""
          }, 
          "startingNode": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Where in the Active Directory directory tree to start monitoring.  If not specified, will attempt to start at the root of the directory tree.", 
            "validation": ""
          }, 
          "targetDc": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies a fully qualified domain name of a valid, network-accessible DC.  If not specified, Splunk will obtain the local computer's DC.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create monitoring stanza."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates new or modifies existing performance monitoring settings.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to Active Directory monitoring input."
  }, 
  "data/inputs/ad/{name}": {
    "methods": {
      "DELETE": {
        "config": "admon", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete AD monitoring stanza."
          }, 
          "404": {
            "summary": "AD monitoring stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes a given AD monitoring stanza.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "admon", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view AD monitoring configuration."
          }, 
          "404": {
            "summary": "AD monitoring stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets the current configuration for a given AD monitoring stanza.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "admon", 
        "params": {
          "disabled": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "monitorSubtree": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "startingNode": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "targetDc": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit AD monitoring stanza."
          }, 
          "404": {
            "summary": "AD monitoring stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modifies a given AD monitoring stanza.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/monitor": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view monitored input."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List enabled and disabled monitor inputs.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "blacklist": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a regular expression for a file path. The file path that matches this regular expression is not indexed.", 
            "validation": ""
          }, 
          "check-index": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If set to true, the \"index\" value will be checked to ensure that it is the name of a valid index.", 
            "validation": "is_bool('check-index')"
          }, 
          "check-path": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If set to true, the \"name\" value will be checked to ensure that it exists.", 
            "validation": "is_bool('check-path')"
          }, 
          "crc-salt": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A string that modifies the file tracking identity for files in this input.  The magic value \"<SOURCE>\" invokes special behavior (see admin documentation).", 
            "validation": ""
          }, 
          "followTail": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If set to true, files that are seen for the first time will be read from the end.", 
            "validation": "is_bool('followTail')"
          }, 
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value to populate in the host field for events from this data input.", 
            "validation": ""
          }, 
          "host_regex": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a regular expression for a file path. If the path for a file matches this regular expression, the captured value is used to populate the host field for events from this data input.  The regular expression must have one capture group.", 
            "validation": ""
          }, 
          "host_segment": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Use the specified slash-separate segment of the filepath as the host field value.", 
            "validation": "is_pos_int('host_segment')"
          }, 
          "ignore-older-than": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a time value. If the modification time of a file being monitored falls outside of this rolling time window, the file is no longer being monitored.", 
            "validation": "validate(match('ignore-older-than', \"^\\\\d+[dms]$\"),\"'Ignore older than' must be a number immediately followed by d(ays), m(inutes), or s(econds).\")"
          }, 
          "index": {
            "datatype": "String", 
            "default": "default", 
            "required": "false", 
            "summary": "Which index events from this input should be stored in.", 
            "validation": "is_index('index')"
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The file or directory path to monitor on the system.", 
            "validation": "validate(len(name) < 4096, 'Must be less than 4096 characters.')"
          }, 
          "recursive": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Setting this to \"false\" will prevent monitoring of any subdirectories encountered within this data input.", 
            "validation": "is_bool('recursive')"
          }, 
          "rename-source": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value to populate in the source field for events from this data input.  The same source should not be used for multiple data inputs.", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value to populate in the sourcetype field for incoming events.", 
            "validation": ""
          }, 
          "time-before-close": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "When Splunk reaches the end of a file that is being read, the file will be kept open for a minimum of the number of seconds specified in this value.  After this period has elapsed, the file will be checked again for more data.", 
            "validation": "is_pos_int('time-before-close')"
          }, 
          "whitelist": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a regular expression for a file path. Only file paths that match this regular expression are indexed.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create monitored input."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a new file or directory monitor input.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to monitor inputs."
  }, 
  "data/inputs/monitor/{name}": {
    "methods": {
      "DELETE": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete monitored input."
          }, 
          "404": {
            "summary": "Monitored input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Disable the named monitor data input and remove it from the configuration.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view monitored input."
          }, 
          "404": {
            "summary": "Monitored input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List the properties of a single monitor data input.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "blacklist": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "check-index": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "is_bool('check-index')"
          }, 
          "check-path": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "is_bool('check-path')"
          }, 
          "crc-salt": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "followTail": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "is_bool('followTail')"
          }, 
          "host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "host_regex": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "host_segment": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "is_pos_int('host_segment')"
          }, 
          "ignore-older-than": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(match('ignore-older-than', \"^\\\\d+[dms]$\"),\"'Ignore older than' must be a number immediately followed by d(ays), m(inutes), or s(econds).\")"
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "default", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "is_index('index')"
          }, 
          "recursive": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "is_bool('recursive')"
          }, 
          "rename-source": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "time-before-close": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "is_pos_int('time-before-close')"
          }, 
          "whitelist": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit monitored input."
          }, 
          "404": {
            "summary": "Monitored input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Update properties of the named monitor input.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/monitor/{name}/members": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view monitored input's files."
          }, 
          "404": {
            "summary": "Monitor input does not exist or does not have any members."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists all files monitored under the named monitor input.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/oneshot": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view inputs."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Enumerates in-progress oneshot inputs. As soon as an input is complete, it is removed from this list.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value of the \"host\" field to be applied to data from this file.", 
            "validation": ""
          }, 
          "host_regex": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A regex to be used to extract a \"host\" field from the path.\n\nIf the path matches this regular expression, the captured value is used to populate the host field for events from this data input. The regular expression must have one capture group.", 
            "validation": ""
          }, 
          "host_segment": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Use the specified slash-separate segment of the path as the host field value.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The destination index for data processed from this file.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The path to the file to be indexed. The file must be locally accessible by the server.", 
            "validation": ""
          }, 
          "rename-source": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value of the \"source\" field to be applied to data from this file.", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value of the \"sourcetype\" field to be applied to data from this file.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create input."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Queues a file for immediate indexing by the file input subsystem. The file must be locally accessible from the server.\n\nThis endpoint can handle any single file: plain, compressed or archive. The file is indexed in full, regardless of whether it has been indexed before.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to oneshot inputs."
  }, 
  "data/inputs/oneshot/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Finds information about a single in-flight one shot input. This is a subset of the information in the full enumeration.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/registry": {
    "methods": {
      "GET": {
        "config": "regmon-filters", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Boolean predicate to filter results.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc | desc)\n\nIndicates whether to sort the entries returned in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to sort by.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto | alpha | alpha_case | num)\n\nIndicates the collating sequence for sorting the returned entries.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view registry monitoring configuration."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets current registry monitoring configuration.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "regmon-filters", 
        "params": {
          "baseline": {
            "datatype": "Number", 
            "default": "0", 
            "required": "true", 
            "summary": "Specifies whether or not to establish a baseline value for the registry keys.  1 means yes, 0 no.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "1", 
            "required": "false", 
            "summary": "Indicates whether the monitoring is disabled.", 
            "validation": ""
          }, 
          "hive": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Specifies the registry hive under which to monitor for changes.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The index in which to store the gathered data.", 
            "validation": ""
          }, 
          "monitorSubnodes": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "If set to '1', will monitor all sub-nodes under a given hive.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Name of the configuration stanza.", 
            "validation": ""
          }, 
          "proc": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Specifies a regex.  If specified, will only collected changes if a process name matches that regex.", 
            "validation": ""
          }, 
          "type": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "A regular expression that specifies the type(s) of Registry event(s) that you want to monitor.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create registry monitoring stanza."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates new or modifies existing registry monitoring settings.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to Windows registry monitoring input."
  }, 
  "data/inputs/registry/{name}": {
    "methods": {
      "DELETE": {
        "config": "regmon-filters", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete registry configuration stanza."
          }, 
          "404": {
            "summary": "Registry monitoring configuration stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes registry monitoring configuration stanza.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "regmon-filters", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view registry monitoring configuration stanza."
          }, 
          "404": {
            "summary": "Registry monitoring stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets current registry monitoring configuration stanza.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "regmon-filters", 
        "params": {
          "baseline": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "hive": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "monitorSubnodes": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "proc": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "type": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit registry monitoring stanza."
          }, 
          "404": {
            "summary": "Registry monitoring stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modifies given registry monitoring stanza.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/script": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view script."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets the configuration settings for scripted inputs.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies whether the input script is disabled.", 
            "validation": ""
          }, 
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the host for events from this input. Defaults to whatever host sent the event.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "default", 
            "required": "false", 
            "summary": "Sets the index for events from this input. Defaults to the main index.", 
            "validation": "is_index(index)"
          }, 
          "interval": {
            "datatype": "Number", 
            "default": "60", 
            "required": "true", 
            "summary": "Specify an integer or cron schedule. This parameter specifies how often to execute the specified script, in seconds or a valid cron schedule. If you specify a cron schedule, the script is not executed on start-up.", 
            "validation": "isint(interval)OR is_cron(interval)"
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Specify the name of the scripted input.", 
            "validation": ""
          }, 
          "passAuth": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "User to run the script as.\n\nIf you provide a username, Splunk generates an auth token for that user and passes it to the script.", 
            "validation": ""
          }, 
          "rename-source": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a new name for the source field for the script.", 
            "validation": ""
          }, 
          "source": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the source key/field for events from this input. Defaults to the input file path.\n\nSets the source key's initial value. The key is used during parsing/indexing, in particular to set the source field during indexing.  It is also the source field used at search time. As a convenience, the chosen string is prepended with 'source::'.\n\nNote: Overriding the source key is generally not recommended.  Typically, the input layer provides a more accurate string to aid in problem analysis and investigation, accurately recording the file  from which the data was retreived. Consider use of source types, tagging, and search wildcards before overriding this value.\n\n", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the sourcetype key/field for events from this input. If unset, Splunk picks a source type based on various aspects of the data. As a convenience, the chosen string is prepended with 'sourcetype::'. There is no hard-coded default.\n\nSets the sourcetype key's initial value. The key is used during parsing/indexing, in particular to set the source type field during indexing. It is also the source type field used at search time.\n\nPrimarily used to explicitly declare the source type for this data, as opposed to allowing it to be determined via automated methods.  This is typically important both for searchability and for applying the relevant configuration for this type of data during parsing and indexing.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create script."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Configures settings for new scripted inputs.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to scripted inputs."
  }, 
  "data/inputs/script/restart": {
    "methods": {
      "POST": {
        "config": "inputs", 
        "params": {
          "script": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Path to the script to be restarted.  This path must match an already-configured existing scripted input.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Scripted input restarted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to restart scripted input."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Causes a restart on a given scripted input.", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for restarting scripted inputs."
  }, 
  "data/inputs/script/{name}": {
    "methods": {
      "DELETE": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete script."
          }, 
          "404": {
            "summary": "Script does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Removes the scripted input specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view script."
          }, 
          "404": {
            "summary": "Script does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the configuration settings for the scripted input specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "default", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "is_index(index)"
          }, 
          "interval": {
            "datatype": "INHERITED", 
            "default": "60", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "isint(interval)OR is_cron(interval)"
          }, 
          "passAuth": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "rename-source": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "source": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit script."
          }, 
          "404": {
            "summary": "Script does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Configures settings for scripted input specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/tcp/cooked": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view inputs."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information about all cooked TCP inputs.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "SSL": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If SSL is not already configured, error is returned", 
            "validation": ""
          }, 
          "connection_host": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (ip &#124; dns &#124; none)\n\nSet the host for the remote server that is sending data.\n\n<code>ip</code> sets the host to the IP address of the remote server sending data.\n\n<code>dns</code> sets the host to the reverse DNS entry for the IP address of the remote server sending data. \n\n<code>none</code> leaves the host as specified in inputs.conf, which is typically the Splunk system hostname.\n\nDefault value is <code>ip</code>.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the input is disabled.", 
            "validation": ""
          }, 
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The default value to fill in for events lacking a host value.", 
            "validation": ""
          }, 
          "port": {
            "datatype": "Number", 
            "default": "", 
            "required": "true", 
            "summary": "The port number of this input.", 
            "validation": ""
          }, 
          "restrictToHost": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Restrict incoming connections on this port to the host specified here.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Some arguments were invalid"
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create input."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "There was an error; see body contents for messages"
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a new container for managing cooked data.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to tcp inputs from forwarders.\n\nForwarders can transmit three types of data: raw, unparsed, or parsed. Cooked data refers to parsed and unparsed formats."
  }, 
  "data/inputs/tcp/cooked/{name}": {
    "methods": {
      "DELETE": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Removes the cooked TCP inputs for port or host:port specified by <code>{name}</code>", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "OK"
          }, 
          "400": {
            "summary": "''TO DO: provide the rest of the status codes''"
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information for the cooked TCP input specified by <code>{name}</code>.\n\nIf port is restricted to a host, name should be URI-encoded host:port.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "SSL": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "connection_host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "restrictToHost": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the container for managaing cooked data.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/tcp/cooked/{name}/connections": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed connections successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input's connections."
          }, 
          "404": {
            "summary": "TCP input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Retrieves list of active connections to the named port.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/tcp/raw": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information about all raw TCP inputs.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "SSL": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "", 
            "validation": ""
          }, 
          "connection_host": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (ip &#124; dns &#124; none)\n\nSet the host for the remote server that is sending data.\n\n<code>ip</code> sets the host to the IP address of the remote server sending data.\n\n<code>dns</code> sets the host to the reverse DNS entry for the IP address of the remote server sending data. \n\n<code>none</code> leaves the host as specified in inputs.conf, which is typically the Splunk system hostname.\n\nDefault value is <code>ip</code>.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the inputs are disabled.", 
            "validation": ""
          }, 
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The host from which the indexer gets data.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "default", 
            "required": "false", 
            "summary": "The index in which to store all generated events.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The input port which splunk receives raw data in.", 
            "validation": ""
          }, 
          "queue": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (parsingQueue &#124; indexQueue)\n\nSpecifies where the input processor should deposit the events it reads. Defaults to parsingQueue.\n\nSet queue to <code>parsingQueue</code> to apply props.conf and other parsing rules to your data.  For more information about props.conf and rules for timestamping and linebreaking, refer to <code>props.conf</code> and the online documentation at [[Documentation:Splunk:Data:Editinputs.conf Edit inputs.conf]]\n\nSet queue to <code>indexQueue</code> to send your data directly into the index.", 
            "validation": ""
          }, 
          "rawTcpDoneTimeout": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies in seconds the timeout value for adding a Done-key. Default value is 10 seconds.\n\nIf a connection over the port specified by <code>name</code> remains idle after receiving data for specified number of seconds, it adds a Done-key. This implies the last event has been completely received.", 
            "validation": ""
          }, 
          "restrictToHost": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Allows for restricting this input to only accept data from the host specified here.", 
            "validation": ""
          }, 
          "source": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the source key/field for events from this input. Defaults to the input file path.\n\nSets the source key's initial value. The key is used during parsing/indexing, in particular to set the source field during indexing. It is also the source field used at search time. As a convenience, the chosen string is prepended with 'source::'.\n\n'''Note:''' Overriding the source key is generally not recommended.Typically, the input layer provides a more accurate string to aid in problem analysis and investigation, accurately recording the file from which the data was retreived. Consider use of source types, tagging, and search wildcards before overriding this value.", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Set the source type for events from this input.\n\n\"sourcetype=\" is automatically prepended to <string>.\n\nDefaults to audittrail (if signedaudit=true) or fschange (if signedaudit=false).", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Some arguments were invalid"
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create input."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "There was an error; see body contents for messages"
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a new data input for accepting raw TCP data.", 
        "urlParams": {}
      }
    }, 
    "summary": "Container for managing raw tcp inputs from forwarders.\n\nForwarders can tramsmit three types of data: raw, unparsed, or parsed. Cooked data refers to parsed and unparsed formats."
  }, 
  "data/inputs/tcp/raw/{name}": {
    "methods": {
      "DELETE": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Removes the raw inputs for port or host:port specified by <code>{name}</code>", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "OK"
          }, 
          "400": {
            "summary": "''TO DO: provide the rest of the status codes''"
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information about raw TCP input port <code>{name}</code>.\n\nIf port is restricted to a host, name should be URI-encoded host:port.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "SSL": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "connection_host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "default", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "queue": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "rawTcpDoneTimeout": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "restrictToHost": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "source": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit input."
          }, 
          "404": {
            "summary": "Inpuat does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the container for managing raw data.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/tcp/raw/{name}/connections": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed connections successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input's connections."
          }, 
          "404": {
            "summary": "TCP input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "View all connections to the named data input.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/tcp/ssl": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view inputs."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns SSL configuration. There is only one SSL configuration for all input ports.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the SSL configuration of a Splunk server."
  }, 
  "data/inputs/tcp/ssl/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the SSL configuration for the host {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the inputs are disabled.", 
            "validation": ""
          }, 
          "password": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Server certifcate password, if any.", 
            "validation": ""
          }, 
          "requireClientCert": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Determines whether a client must authenticate.", 
            "validation": ""
          }, 
          "rootCA": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Certificate authority list (root file)", 
            "validation": ""
          }, 
          "serverCert": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Full path to the server certificate.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Configures SSL attributes for the host {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/udp": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view inputs."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List enabled and disabled UDP data inputs.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "connection_host": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (ip &#124; dns &#124; none)\n\nSet the host for the remote server that is sending data.\n\n<code>ip</code> sets the host to the IP address of the remote server sending data.\n\n<code>dns</code> sets the host to the reverse DNS entry for the IP address of the remote server sending data. \n\n<code>none</code> leaves the host as specified in inputs.conf, which is typically the Splunk system hostname.\n\nDefault value is <code>ip</code>.", 
            "validation": ""
          }, 
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value to populate in the host field for incoming events. \n\nThis is used during parsing/indexing, in particular to set the host field. It is also the host field used at search time.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "default", 
            "required": "false", 
            "summary": "Which index events from this input should be stored in.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The UDP port that this input should listen on.", 
            "validation": "is_avail_udp_port(name)"
          }, 
          "no_appending_timestamp": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If set to true, prevents Splunk from prepending a timestamp and hostname to incoming events.", 
            "validation": ""
          }, 
          "no_priority_stripping": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If set to true, Splunk will not remove the priority field from incoming syslog events.", 
            "validation": ""
          }, 
          "queue": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Which queue events from this input should be sent to.  Generally this does not need to be changed.", 
            "validation": ""
          }, 
          "restrictToHost": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Restrict incoming connections on this port to the host specified here.\n\nIf this is not set, the value specified in [udp://<remote server>:<port>] in inputs.conf is used.", 
            "validation": ""
          }, 
          "source": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value to populate in the source field for incoming events.  The same source should not be used for multiple data inputs.", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value to populate in the sourcetype field for incoming events.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create input."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a new UDP data input.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to UPD data inputs."
  }, 
  "data/inputs/udp/{name}": {
    "methods": {
      "DELETE": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Disable the named UDP data input and remove it from the configuration.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input configuration."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List the properties of a single UDP data input port or host:port <code>{name}</code>.\nIf port is restricted to a host, name should be URI-encoded host:port.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "connection_host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "default", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "no_appending_timestamp": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "no_priority_stripping": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "queue": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "restrictToHost": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "source": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit input."
          }, 
          "404": {
            "summary": "Input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Edit properties of the named UDP data input.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/udp/{name}/connections": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed connections successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view input connections."
          }, 
          "404": {
            "summary": "UDP input does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists connections to the named UDP input.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/win-event-log-collections": {
    "methods": {
      "GET": {
        "config": "inputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "lookup_host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "For internal use.  Used by the UI when editing the initial host from which we gather event log data.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Boolean predicate to filter results.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc | desc)\n\nIndicates whether to sort the entries returned in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to sort by.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto | alpha | alpha_case | num)\n\nIndicates the collating sequence for sorting the returned entries.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view event log collections."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Retrieves a list of configured event log collections.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "hosts": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A comma-separated list of addtional hosts to be used for monitoring.  The first host should be specified with \"lookup_host\", and the additional ones using this parameter.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "default", 
            "required": "false", 
            "summary": "The index in which to store the gathered data.", 
            "validation": ""
          }, 
          "logs": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A comma-separated list of event log names to gather data from.", 
            "validation": ""
          }, 
          "lookup_host": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "This is a host from which we will monitor log events.  To specify additional hosts to be monitored via WMI, use the \"hosts\" parameter.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "This is the name of the collection.  This name will appear in configuration file, as well as the source and the sourcetype of the indexed data.  If the value is \"localhost\", it will use native event log collection; otherwise, it will use WMI.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create event log collections."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates of modifies existing event log collection settings.  You can configure both native and WMI collection with this endpoint.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to all configured event log collections."
  }, 
  "data/inputs/win-event-log-collections/{name}": {
    "methods": {
      "DELETE": {
        "config": "inputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete event log collections."
          }, 
          "404": {
            "summary": "Event log collection does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes a given event log collection.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "wmi", 
        "params": {
          "lookup_host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "For internal use.  Used by the UI when editing the initial host from which we gather event log data.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view event log collections."
          }, 
          "404": {
            "summary": "Event log collection does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets the configuration settings for a given event log collection.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "inputs", 
        "params": {
          "hosts": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "default", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "logs": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "lookup_host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit event log collections."
          }, 
          "404": {
            "summary": "Event log collection does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modifies existing event log collection.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/win-perfmon": {
    "methods": {
      "GET": {
        "config": "perfmon", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Boolean predicate to filter results.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc | desc)\n\nIndicates whether to sort the entries returned in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to sort by.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto | alpha | alpha_case | num)\n\nIndicates the collating sequence for sorting the returned entries.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view performance monitoring configuration."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets current performance monitoring configuration.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "perfmon", 
        "params": {
          "counters": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A comma-separated list of all counters to monitor. A '*' is equivalent to all counters.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Disables a given monitoring stanza.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The index in which to store the gathered data.", 
            "validation": ""
          }, 
          "instances": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Comma-separated list of counter instances.  A '*' is equivalent to all instances.", 
            "validation": ""
          }, 
          "interval": {
            "datatype": "Number", 
            "default": "", 
            "required": "true", 
            "summary": "How frequently to poll the performance counters.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "This is the name of the collection.  This name will appear in configuration file, as well as the source and the sourcetype of the indexed data.", 
            "validation": ""
          }, 
          "object": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "A valid performance monitor object (for example, 'Process,' 'Server,' 'PhysicalDisk.')", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create monitoring stanza."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates new or modifies existing performance monitoring collection settings.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to performance monitoring configuration.  This input allows you to poll Windows performance monitor counters."
  }, 
  "data/inputs/win-perfmon/{name}": {
    "methods": {
      "DELETE": {
        "config": "perfmon", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete monitoring stanza."
          }, 
          "404": {
            "summary": "Monitoring stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes a given monitoring stanza.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "perfmon", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view configuration settings."
          }, 
          "404": {
            "summary": "Performance stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets settings for a given perfmon stanza.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "perfmon", 
        "params": {
          "counters": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "instances": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "interval": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "object": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit monitoring stanza."
          }, 
          "404": {
            "summary": "Monitoring stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modifies existing monitoring stanza", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/inputs/win-wmi-collections": {
    "methods": {
      "GET": {
        "config": "wmi", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Boolean predicate to filter results.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc | desc)\n\nIndicates whether to sort the entries returned in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to sort by.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto | alpha | alpha_case | num)\n\nIndicates the collating sequence for sorting the returned entries.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view collections."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Provides access to all configure WMI collections.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "wmi", 
        "params": {
          "classes": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "A valid WMI class name.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Disables the given collection.", 
            "validation": ""
          }, 
          "fields": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A comma-separated list of all properties that you want to gather from the given class.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The index in which to store the gathered data.", 
            "validation": ""
          }, 
          "instances": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Instances of a given class for which data is gathered.\n\nSpecify each instance as a separate argument to the POST operation.", 
            "validation": ""
          }, 
          "interval": {
            "datatype": "Number", 
            "default": "", 
            "required": "true", 
            "summary": "The interval at which the WMI provider(s) will be queried.", 
            "validation": ""
          }, 
          "lookup_host": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "This is the server from which we will be gathering WMI data.  If you need to gather data from more than one machine, additional servers can be specified in the 'server' parameter.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "This is the name of the collection.  This name will appear in configuration file, as well as the source and the sourcetype of the indexed data.", 
            "validation": ""
          }, 
          "server": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A comma-separated list of additional servers that you want to gather data from.  Use this if you need to gather from more than a single machine.  See also lookup_host parameter.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create this collection."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates or modifies existing WMI collection settings.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to all configured WMI collections."
  }, 
  "data/inputs/win-wmi-collections/{name}": {
    "methods": {
      "DELETE": {
        "config": "wmi", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete a given collection."
          }, 
          "404": {
            "summary": "Given collection does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes a given collection.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "wmi", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view WMI collections."
          }, 
          "404": {
            "summary": "Given collection does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Gets information about a single collection.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "wmi", 
        "params": {
          "classes": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "fields": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "index": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "instances": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "interval": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "lookup_host": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "server": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit collection."
          }, 
          "404": {
            "summary": "Collection does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modifies a given WMI collection.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/lookup-table-files": {
    "methods": {
      "GET": {
        "config": "lookups", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view lookup-table file."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List lookup table files.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "lookups", 
        "params": {
          "eai:data": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Move a lookup table file from the given path into $SPLUNK_HOME. This path must have the lookup staging area as an ancestor.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The lookup table filename.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create lookup-table file."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a lookup table file by moving a file from the upload staging area into $SPLUNK_HOME.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to lookup table files."
  }, 
  "data/lookup-table-files/{name}": {
    "methods": {
      "DELETE": {
        "config": "lookups", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete look-up table file."
          }, 
          "404": {
            "summary": "Look-up table file does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete the named lookup table file.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "lookups", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view look-up table files."
          }, 
          "404": {
            "summary": "Look-up table file does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List a single lookup table file.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "lookups", 
        "params": {
          "eai:data": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit look-up tble file."
          }, 
          "404": {
            "summary": "Look-up table file does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modify a lookup table file by replacing it with a file from the upload staging area.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/outputs/tcp/default": {
    "methods": {
      "GET": {
        "config": "outputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view outputs."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the current tcpout properties.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "outputs", 
        "params": {
          "defaultGroup": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Comma-separated list of one or more target group names, specified later in [tcpout:<target_group>] stanzas of outputs.conf.spec file.\n\nThe forwarder sends all data to the specified groups. If you don't want to forward data automatically, don't set this attribute. Can be overridden by an inputs.conf _TCP_ROUTING setting, which in turn can be overridden by a props.conf/transforms.conf modifier.\n\nStarting with 4.2, this attribute is no longer required.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Disables default tcpout settings", 
            "validation": ""
          }, 
          "dropEventsOnQueueFull": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "If set to a positive number, wait the specified number of seconds before throwing out all new events until the output queue has space. Defaults to -1 (do not drop events).\n\nCAUTION: Do not set this value to a positive integer if you are monitoring files.\n\nSetting this to -1 or 0 causes the output queue to block when it gets full, whih causes further blocking up the processing chain. If any target group's queue is blocked, no more data reaches any other target group.\n\nUsing auto load-balancing is the best way to minimize this condition, because, in that case, multiple receivers must be down (or jammed up) before queue blocking can occur.", 
            "validation": ""
          }, 
          "heartbeatFrequency": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "How often (in seconds) to send a heartbeat packet to the receiving server.\n\nHeartbeats are only sent if sendCookedData=true. Defaults to 30 seconds.", 
            "validation": ""
          }, 
          "indexAndForward": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies whether to index all data locally, in addition to forwarding it. Defaults to false.\n\nThis is known as an \"index-and-forward\" configuration. This attribute is only available for heavy forwarders. It is available only at the top level [tcpout] stanza in outputs.conf. It cannot be overridden in a target group.", 
            "validation": ""
          }, 
          "maxQueueSize": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Specify an integer or integer[KB|MB|GB].\n\nSets the maximum size of the forwarder's output queue. It also sets the maximum size of the wait queue to 3x this value, if you have enabled indexer acknowledgment (useACK=true).\n\nAlthough the wait queue and the output queues are both configured by this attribute, they are separate queues. The setting determines the maximum size of the queue's in-memory (RAM) buffer.\n\nFor heavy forwarders sending parsed data, maxQueueSize is the maximum number of events. Since events are typically much shorter than data blocks, the memory consumed by the queue on a parsing forwarder will likely be much smaller than on a non-parsing forwarder, if you use this version of the setting.\n\nIf specified as a lone integer (for example, maxQueueSize=100), maxQueueSize indicates the maximum number of queued events (for parsed data) or blocks of data (for unparsed data). A block of data is approximately 64KB. For non-parsing forwarders, such as universal forwarders, that send unparsed data, maxQueueSize is the maximum number of data blocks.\n\nIf specified as an integer followed by KB, MB, or GB (for example, maxQueueSize=100MB), maxQueueSize indicates the maximum RAM allocated to the queue buffer. Defaults to 500KB (which means a maximum size of 500KB for the output queue and 1500KB for the wait queue, if any).", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Configuration to be edited.  The only valid value is \"tcpout\".", 
            "validation": ""
          }, 
          "sendCookedData": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, events are cooked (have been processed by Splunk). If false, events are raw and untouched prior to sending. Defaults to true.\n\nSet to false if you are sending to a third-party system.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create output."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Configures global tcpout properties.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to global TCP out properties."
  }, 
  "data/outputs/tcp/default/{name}": {
    "methods": {
      "DELETE": {
        "config": "outputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to disable forwarding settings."
          }, 
          "404": {
            "summary": "Forwarding settings do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Disable the default forwarding settings.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "outputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view forwaring settings."
          }, 
          "404": {
            "summary": "Forwarding settings do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Retrieve the named configuration.  The only valid name here is \"tcpout\".", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "outputs", 
        "params": {
          "defaultGroup": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dropEventsOnQueueFull": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "heartbeatFrequency": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "indexAndForward": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "maxQueueSize": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sendCookedData": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit forwarding settings."
          }, 
          "404": {
            "summary": "Forwarding settings do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Configure global forwarding properties.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/outputs/tcp/group": {
    "methods": {
      "GET": {
        "config": "outputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view group."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns configuration information about target groups. ", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "outputs", 
        "params": {
          "autoLB": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "If set to true, forwarder performs automatic load balancing. In automatic mode, the forwarder selects a new indexer every autoLBFrequency seconds. If the connection to the current indexer is lost, the forwarder selects a new live indexer to forward data to.\n\nDo not alter the default setting, unless you have some overriding need to use round-robin load balancing. Round-robin load balancing (autoLB=false) was previously the default load balancing method. Starting with release 4.2, however, round-robin load balancing has been deprecated, and the default has been changed to automatic load balancing (autoLB=true).", 
            "validation": ""
          }, 
          "compressed": {
            "datatype": "Boolean", 
            "default": "false", 
            "required": "false", 
            "summary": "If true, forwarder sends compressed data.\n\nIf set to true, the receiver port must also have compression turned on.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "false", 
            "required": "false", 
            "summary": "If true, disables the group.", 
            "validation": ""
          }, 
          "dropEventsOnQueueFull": {
            "datatype": "Number", 
            "default": "-1", 
            "required": "false", 
            "summary": "If set to a positive number, wait the specified number of seconds before throwing out all new events until the output queue has space. Defaults to -1 (do not drop events).\n\nCAUTION: Do not set this value to a positive integer if you are monitoring files.\n\nSetting this to -1 or 0 causes the output queue to block when it gets full, which causes further blocking up the processing chain. If any target group's queue is blocked, no more data reaches any other target group.\n\nUsing auto load-balancing is the best way to minimize this condition, because, in that case, multiple receivers must be down (or jammed up) before queue blocking can occur.", 
            "validation": ""
          }, 
          "heartbeatFrequency": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "How often (in seconds) to send a heartbeat packet to the group.\n\nHeartbeats are only sent if sendCookedData=true. Defaults to 30 seconds.", 
            "validation": ""
          }, 
          "maxQueueSize": {
            "datatype": "Number", 
            "default": "500KB", 
            "required": "false", 
            "summary": "Specify either an integer or integer[KB&#124;MB&#124;GB].\n\nSets the maximum size of the forwarder's output queue. It also sets the maximum size of the wait queue to 3x this value, if you have enabled indexer acknowledgment (useACK=true).\n\nAlthough the wait queue and the output queues are both configured by this attribute, they are separate queues. The setting determines the maximum size of the queue's in-memory (RAM) buffer.\n\nFor heavy forwarders sending parsed data, maxQueueSize is the maximum number of events. Since events are typically much shorter than data blocks, the memory consumed by the queue on a parsing forwarder will likely be much smaller than on a non-parsing forwarder, if you use this version of the setting.\n\nIf specified as a lone integer (for example, maxQueueSize=100), maxQueueSize indicates the maximum number of queued events (for parsed data) or blocks of data (for unparsed data). A block of data is approximately 64KB. For non-parsing forwarders, such as universal forwarders, that send unparsed data, maxQueueSize is the maximum number of data blocks.\n\nIf specified as an integer followed by KB, MB, or GB (for example, maxQueueSize=100MB), maxQueueSize indicates the maximum RAM allocated to the queue buffer. Defaults to 500KB (which means a maximum size of 500KB for the output queue and 1500KB for the wait queue, if any).", 
            "validation": ""
          }, 
          "method": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (tcpout &#124; syslog)\n\nSpecifies the type of output processor.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the group of receivers.", 
            "validation": ""
          }, 
          "sendCookedData": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "If true, send cooked events (events that have been processed by Splunk).\n\nIf false, events are raw and untouched prior to sending. Set to false if you are sending to a third-party system.\n\nDefaults to true.", 
            "validation": ""
          }, 
          "servers": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Comma-separated list of servers to include in the group.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create group."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Configures a group of one or more data forwarding destinations.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the configuration of a group of one or more data forwarding destinations."
  }, 
  "data/outputs/tcp/group/{name}": {
    "methods": {
      "DELETE": {
        "config": "outputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete group."
          }, 
          "404": {
            "summary": "Group does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes the target group specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "outputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view group."
          }, 
          "404": {
            "summary": "Group does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns configuration information about the target group specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "outputs", 
        "params": {
          "autoLB": {
            "datatype": "INHERITED", 
            "default": "true", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "compressed": {
            "datatype": "INHERITED", 
            "default": "false", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "false", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dropEventsOnQueueFull": {
            "datatype": "INHERITED", 
            "default": "-1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "heartbeatFrequency": {
            "datatype": "INHERITED", 
            "default": "30", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "maxQueueSize": {
            "datatype": "INHERITED", 
            "default": "500KB", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "method": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sendCookedData": {
            "datatype": "INHERITED", 
            "default": "true", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "servers": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit group."
          }, 
          "404": {
            "summary": "Group does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the configuration of the target group.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/outputs/tcp/server": {
    "methods": {
      "GET": {
        "config": "outputs", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view forwarded servers."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists existing forwarded servers.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "outputs", 
        "params": {
          "backoffAtStartup": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Sets in seconds how long to wait to retry the first time a retry is needed. Compare to initialBackoff.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, disables the forwarder.", 
            "validation": ""
          }, 
          "initialBackoff": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Sets how long, in seconds, to wait to retry every time after the first retry. Compare to backoffAtStartup.", 
            "validation": ""
          }, 
          "maxBackoff": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies the number of times in seconds before reaching the maximum backoff frequency.", 
            "validation": ""
          }, 
          "maxNumberOfRetriesAtHighestBackoff": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies the number of times the system should retry after reaching the highest back-off period, before stopping completely. -1 (default value) means to try forever.\n\nCaution: Splunk recommends that you not change this from the default, or the forwarder will completely stop forwarding to a downed URI at some point.\n", 
            "validation": ""
          }, 
          "method": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (clone &#124; balance &#124; autobalance)\n\nThe data distribution method used when two or more servers exist in the same forwarder group.  ", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "<host>:<port> of the Splunk receiver. <host> can be either an ip address or server name. <port> is the that port that the Splunk receiver is listening on.", 
            "validation": ""
          }, 
          "sslAltNameToCheck": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The alternate name to match in the remote server's SSL certificate.", 
            "validation": ""
          }, 
          "sslCertPath": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Path to the client certificate. If specified, connection uses SSL.", 
            "validation": ""
          }, 
          "sslCipher": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "SSL Cipher in the form ALL:!aNULL:!eNULL:!LOW:!EXP:RC4+RSA:+HIGH:+MEDIUM", 
            "validation": ""
          }, 
          "sslCommonNameToCheck": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Check the common name of the server's certificate against this name.\n\nIf there is no match, assume that Splunk is not authenticated against this server. You must specify this setting if sslVerifyServerCert is true.", 
            "validation": ""
          }, 
          "sslPassword": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The password associated with the CAcert.\n\nThe default Splunk CAcert uses the password \"password.\"", 
            "validation": ""
          }, 
          "sslRootCAPath": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The path to the root certificate authority file (optional).", 
            "validation": ""
          }, 
          "sslVerifyServerCert": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": " If true, make sure that the server you are connecting to is a valid one (authenticated). Both the common name and the alternate name of the server are then checked for a match.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create a forwarded server."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a new forwarder output.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to data forwarding configurations."
  }, 
  "data/outputs/tcp/server/{name}": {
    "methods": {
      "DELETE": {
        "config": "outputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete forwarded server configuration."
          }, 
          "404": {
            "summary": "Forwarded server does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes the configuration for the forwarded server specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "outputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view forwarded server."
          }, 
          "404": {
            "summary": "Forwarded server does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists information aobut the forwarded server specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "outputs", 
        "params": {
          "backoffAtStartup": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "initialBackoff": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "maxBackoff": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "maxNumberOfRetriesAtHighestBackoff": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "method": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sslAltNameToCheck": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sslCertPath": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sslCipher": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sslCommonNameToCheck": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sslPassword": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sslRootCAPath": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "sslVerifyServerCert": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit configuratin for forwarded server."
          }, 
          "404": {
            "summary": "Forwarded server does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Configures the forwarded server specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/outputs/tcp/server/{name}/allconnections": {
    "methods": {
      "GET": {
        "config": "outputs", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed connections successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to list ouput connections."
          }, 
          "404": {
            "summary": "Output server does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List current connections to forwarded server specified by {name} ", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/outputs/tcp/syslog": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view configuration of forwarded servers."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Provides access to syslog data forwarding configurations.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, disables global syslog settings.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Name of the forwarder to send data in standard syslog format.", 
            "validation": ""
          }, 
          "priority": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Sets syslog priority value.", 
            "validation": ""
          }, 
          "server": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "host:port of the server where syslog data should be sent", 
            "validation": ""
          }, 
          "timestampformat": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Format of timestamp to add at start of the events to be forwarded.", 
            "validation": ""
          }, 
          "type": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Protocol to use to send syslog data. Valid values: (tcp &#124; udp ).", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to configure a forwarded server."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Configures a forwarder to send data in standard syslog format.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the configuration of a forwarded server configured to provide data in standard syslog format."
  }, 
  "data/outputs/tcp/syslog/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete forwarded server configuration."
          }, 
          "404": {
            "summary": "Forwarded server configuration does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes the configuration for the forwarder specified by {name} that sends data in syslog format.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view forwarded server configuration."
          }, 
          "404": {
            "summary": "Forwarded server does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns configuration information for the forwarder specified by {name} that sends data in standard syslog format.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "priority": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "server": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "timestampformat": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "type": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit forwarded server configuration."
          }, 
          "404": {
            "summary": "Forwarded server does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the configuration of the forwarder specified by {name} that sends data in syslog format.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/props/extractions": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view extractions."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List field extractions.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The user-specified part of the field extraction name. The full name of the field extraction includes this identifier as a suffix.", 
            "validation": ""
          }, 
          "stanza": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The props.conf stanza to which this field extraction applies, e.g. the sourcetype or source that triggers this field extraction. The full name of the field extraction includes this stanza name as a prefix.", 
            "validation": "validate(len(trim($stanza$)) > 0, \"Value of argument 'stanza' may not be empty\")"
          }, 
          "type": {
            "datatype": "Enum", 
            "default": "", 
            "required": "true", 
            "summary": "Valid values: (REPORT &#124; EXTRACT)\n\nAn EXTRACT-type field extraction is defined with an \"inline\" regular expression. A REPORT-type field extraction refers to a transforms.conf stanza.", 
            "validation": "validate(($type$ == 'REPORT') OR ($type$ == 'EXTRACT'), \"Value of 'type' must be one of { REPORT, EXTRACT }\")"
          }, 
          "value": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "If this is an EXTRACT-type field extraction, specify a regular expression with named capture groups that define the desired fields. If this is a REPORT-type field extraction, specify a comma- or space-delimited list of transforms.conf stanza names that define the field transformations to apply.", 
            "validation": "validate(len(trim($value$)) > 0, \"Value of argument 'value' may not be empty\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create extraction."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a new field extraction.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to search-time field extractions in props.conf."
  }, 
  "data/props/extractions/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete named extraction."
          }, 
          "404": {
            "summary": "Named extraction does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete the named field extraction.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view named extraction."
          }, 
          "404": {
            "summary": "Named extraction does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List a single field extraction.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "value": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": "validate(len(trim($value$)) > 0, \"Value of argument 'value' may not be empty\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit named extraction."
          }, 
          "404": {
            "summary": "Named extraction does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modify the named field extraction.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/props/fieldaliases": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view filed aliases."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List field aliases.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "alias.*": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The alias for a given field. For example, supply a value of \"bar\" for an argument \"alias.foo\" to alias \"foo\" to \"bar\".", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The user-specified part of the field alias name. The full name of the field alias includes this identifier as a suffix.", 
            "validation": ""
          }, 
          "stanza": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The props.conf stanza to which this field alias applies, e.g. the sourcetype or source that causes this field alias to be applied. The full name of the field alias includes this stanza name as a prefix.", 
            "validation": "validate(len(trim($stanza$)) > 0, \"Value of argument 'stanza' may not be empty\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create field alias."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a new field alias.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to field aliases in props.conf."
  }, 
  "data/props/fieldaliases/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete field alias."
          }, 
          "404": {
            "summary": "Field alias does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete the named field alias.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view field alias."
          }, 
          "404": {
            "summary": "Field alias does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List a single field alias.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "alias.*": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit field alias."
          }, 
          "404": {
            "summary": "Field alias does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modify the named field alias.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/props/lookups": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view lookups."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List automatic lookups.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "lookup.field.input.*": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A column in the lookup table to match against. Supply a non-empty value if the corresponding field has a different name in your actual events.\n\n'''Note:''' This parameter is new in Splunk 4.3.", 
            "validation": ""
          }, 
          "lookup.field.output.*": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A column in the lookup table to output. Supply a non-empty value if the field should have a different name in your actual events.\n\n'''Note:''' This parameter is new in Splunk 4.3.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The user-specified part of the automatic lookup name. The full name of the automatic lookup includes this identifier as a suffix.", 
            "validation": ""
          }, 
          "overwrite": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "true", 
            "summary": "If set to true, output fields are always overridden. If set to false, output fields are only written out if they do not already exist.", 
            "validation": ""
          }, 
          "stanza": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The props.conf stanza to which this automatic lookup applies, e.g. the sourcetype or source that automatically triggers this lookup. The full name of the automatic lookup includes this stanza name as a prefix.", 
            "validation": "validate(len(trim($stanza$)) > 0, \"Value of argument 'stanza' may not be empty\")"
          }, 
          "transform": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The transforms.conf stanza that defines the lookup to apply.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create a lookup."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a new automatic lookup.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to automatic lookups in props.conf."
  }, 
  "data/props/lookups/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete lookup."
          }, 
          "404": {
            "summary": "Lookup does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete the named automatic lookup.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view lookup."
          }, 
          "404": {
            "summary": "Lookup does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List a single automatic lookup.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "lookup.field.input.*": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "lookup.field.output.*": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "overwrite": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "transform": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit lookup."
          }, 
          "404": {
            "summary": "Lookup does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modify the named automatic lookup.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/props/sourcetype-rename": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view sourcetype renames."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List renamed sourcetypes.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The original sourcetype name.", 
            "validation": ""
          }, 
          "value": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The new sourcetype name.", 
            "validation": "validate(len(trim($value$)) > 0, \"Value of argument 'value' may not be empty\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create a rename for a sourcetype."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Rename a sourcetype.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to renamed sourcetypes which are configured in props.conf."
  }, 
  "data/props/sourcetype-rename/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete the rename for the sourcetype."
          }, 
          "404": {
            "summary": "Rename for the sourcetype does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Restore a sourcetype's original name.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view renames for sourcetypes."
          }, 
          "404": {
            "summary": "Rename for sourcetype does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List a single renamed sourcetype.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "value": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": "validate(len(trim($value$)) > 0, \"Value of argument 'value' may not be empty\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit renames for the sourcetype."
          }, 
          "404": {
            "summary": "Rename for the sourcetype does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Rename a sourcetype again, i.e. modify a sourcetype's new name.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/transforms/extractions": {
    "methods": {
      "GET": {
        "config": "transforms", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view field transformations."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List field transformations.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "transforms", 
        "params": {
          "CAN_OPTIMIZE": {
            "datatype": "Bool", 
            "default": "True", 
            "required": "false", 
            "summary": "Controls whether Splunk can optimize this extraction out (another way of saying the extraction is disabled).  You might use this when you have field discovery turned off--it ensures that certain fields are *always* discovered.  Splunk only disables an extraction if it can determine that none of the fields identified by the extraction will ever be needed for the successful evaluation of a search.\n\nNOTE: This option should rarely be set to false.", 
            "validation": "validate(is_bool($CAN_OPTIMIZE$), \"Value of argument 'CAN_OPTIMIZE' must be a boolean\")"
          }, 
          "CLEAN_KEYS": {
            "datatype": "Boolean", 
            "default": "True", 
            "required": "false", 
            "summary": "If set to true, Splunk \"cleans\" the field names extracted at search time by replacing non-alphanumeric characters with underscores and stripping leading underscores.", 
            "validation": "validate(is_bool($CLEAN_KEYS$), \"Value of argument 'CLEAN_KEYS' must be a boolean\")"
          }, 
          "FORMAT": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "This option is valid for both index-time and search-time field extractions. However, FORMAT behaves differently depending on whether the extraction is performed at index time or search time.\n\nThis attribute specifies the format of the event, including any field names or values you want to add.\n\nFORMAT for index-time extractions:\n\nUse $n (for example $1, $2, etc) to specify the output of each REGEX match.\n\nIf REGEX does not have n groups, the matching fails.\n\nThe special identifier $0 represents what was in the DEST_KEY before the REGEX was performed.\n\nAt index-time only, you can use FORMAT to create concatenated fields: FORMAT = ipaddress::$1.$2.$3.$4\n\nWhen you create concatenated fields with FORMAT, \"$\" is the only special character. It is treated as a prefix for regex-capturing groups only if it is followed by a number and only if the number applies to an existing capturing group. So if REGEX has only one capturing group and its value is \"bar\", then:\n\\t\"FORMAT = foo$1\" yields \"foobar\"\n\\t\"FORMAT = foo$bar\" yields \"foo$bar\"\n\\t\"FORMAT = foo$1234\" yields \"foo$1234\"\n\\t\"FORMAT = foo$1\\\\$2\" yields \"foobar\\\\$2\"\n\nAt index-time, FORMAT defaults to <stanza-name>::$1\n\nFORMAT for search-time extractions:\n\nThe format of this field as used during search time extractions is as follows:\n\\tFORMAT = <field-name>::<field-value>( <field-name>::<field-value>)*\n\\tfield-name  = [<string>|$<extracting-group-number>]\n\\tfield-value = [<string>|$<extracting-group-number>]\n\nSearch-time extraction examples:\n\\tFORMAT = first::$1 second::$2 third::other-value\n\\tFORMAT = $1::$2\n\nYou cannot create concatenated fields with FORMAT at search time. That functionality is only available at index time.\n\nAt search-time, FORMAT defaults to an empty string.", 
            "validation": ""
          }, 
          "KEEP_EMPTY_VALS": {
            "datatype": "Boolean", 
            "default": "False", 
            "required": "false", 
            "summary": "If set to true, Splunk preserves extracted fields with empty values.", 
            "validation": "validate(is_bool($KEEP_EMPTY_VALS$), \"Value of argument 'KEEP_EMPTY_VALS' must be a boolean\")"
          }, 
          "MV_ADD": {
            "datatype": "Boolean", 
            "default": "False", 
            "required": "false", 
            "summary": "If Splunk extracts a field that already exists and MV_ADD is set to true, the field becomes multivalued, and the newly-extracted value is appended. If MV_ADD is set to false, the newly-extracted value is discarded.", 
            "validation": "validate(is_bool($MV_ADD$), \"Value of argument 'MV_ADD' must be a boolean\")"
          }, 
          "REGEX": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Specify a regular expression to operate on your data.\n\nThis attribute is valid for both index-time and search-time field extractions:\n\\tREGEX is required for all search-time transforms unless you are setting up a delimiter-based field extraction, in which case you use DELIMS (see the DELIMS attribute description, below).\n\\tREGEX is required for all index-time transforms.\n\nREGEX and the FORMAT attribute:\n\nName-capturing groups in the REGEX are extracted directly to fields. This means that you do not need to specify the FORMAT attribute for simple field extraction cases.\n\nIf the REGEX extracts both the field name and its corresponding field value, you can use the following special capturing groups if you want to skip specifying the mapping in FORMAT: _KEY_<string>, _VAL_<string>.\n\nFor example, the following are equivalent:\n\\tUsing FORMAT:\n\\t\\tREGEX  = ([a-z]+)=([a-z]+)\n\\t\\tFORMAT = $1::$2\n\\tWithout using FORMAT\n\\t\\tREGEX  = (?<_KEY_1>[a-z]+)=(?<_VAL_1>[a-z]+)\n\nREGEX defaults to an empty string.", 
            "validation": ""
          }, 
          "SOURCE_KEY": {
            "datatype": "String", 
            "default": "_raw", 
            "required": "true", 
            "summary": "Specify the KEY to which Splunk applies REGEX.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies whether the field transformation is disabled.", 
            "validation": "validate(is_bool($disabled$), \"Value of argument 'disabled' must be a boolean\")"
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the field transformation.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create field transformation."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a new field transformation.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to field transformations, i.e. field extraction definitions."
  }, 
  "data/transforms/extractions/{name}": {
    "methods": {
      "DELETE": {
        "config": "transforms", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete named field transformation."
          }, 
          "404": {
            "summary": "Named field transformation does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete the named field transformation.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "transforms", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view named field transformation."
          }, 
          "404": {
            "summary": "Named field transformation does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List a single field transformation.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "transforms", 
        "params": {
          "CAN_OPTIMIZE": {
            "datatype": "INHERITED", 
            "default": "True", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($CAN_OPTIMIZE$), \"Value of argument 'CAN_OPTIMIZE' must be a boolean\")"
          }, 
          "CLEAN_KEYS": {
            "datatype": "INHERITED", 
            "default": "True", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($CLEAN_KEYS$), \"Value of argument 'CLEAN_KEYS' must be a boolean\")"
          }, 
          "FORMAT": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "KEEP_EMPTY_VALS": {
            "datatype": "INHERITED", 
            "default": "False", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($KEEP_EMPTY_VALS$), \"Value of argument 'KEEP_EMPTY_VALS' must be a boolean\")"
          }, 
          "MV_ADD": {
            "datatype": "INHERITED", 
            "default": "False", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($MV_ADD$), \"Value of argument 'MV_ADD' must be a boolean\")"
          }, 
          "REGEX": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "SOURCE_KEY": {
            "datatype": "INHERITED", 
            "default": "_raw", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($disabled$), \"Value of argument 'disabled' must be a boolean\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit named field transformation."
          }, 
          "404": {
            "summary": "Named field transformation does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modify the named field transformation.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "data/transforms/lookups": {
    "methods": {
      "GET": {
        "config": "transforms", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view lookups."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List lookup definitions.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "transforms", 
        "params": {
          "default_match": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "If min_matches is greater than zero and Splunk has less than min_matches for any given input, it provides this default_match value one or more times until the min_matches threshold is reached.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies whether the lookup definition is disabled.", 
            "validation": "validate(is_bool($disabled$), \"Value of argument 'disabled' must be a boolean\")"
          }, 
          "external_cmd": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Provides the command and arguments to invoke to perform a lookup. Use this for external (or \"scripted\") lookups, where you interface with with an external script rather than a lookup table.", 
            "validation": ""
          }, 
          "fields_list": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A comma- and space-delimited list of all fields that are supported by the external command. Use this for external (or \"scripted\") lookups.", 
            "validation": ""
          }, 
          "filename": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The name of the static lookup table file.", 
            "validation": ""
          }, 
          "max_matches": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "The maximum number of possible matches for each input lookup value.", 
            "validation": ""
          }, 
          "max_offset_secs": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "For temporal lookups, this is the maximum time (in seconds) that the event timestamp can be later than the lookup entry time for a match to occur.", 
            "validation": ""
          }, 
          "min_matches": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "The minimum number of possible matches for each input lookup value.", 
            "validation": ""
          }, 
          "min_offset_secs": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "For temporal lookups, this is the minimum time (in seconds) that the event timestamp can be later than the lookup entry timestamp for a match to occur.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the lookup definition.", 
            "validation": ""
          }, 
          "time_field": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "For temporal lookups, this is the field in the lookup table that represents the timestamp.", 
            "validation": ""
          }, 
          "time_format": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "For temporal lookups, this specifies the \"strptime\" format of the timestamp field.", 
            "validation": "validate(is_time_format($time_format$), \"Value of argument 'time_format' must be a time format string\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create lookup."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a new lookup definition.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to lookup definitions in transforms.conf."
  }, 
  "data/transforms/lookups/{name}": {
    "methods": {
      "DELETE": {
        "config": "transforms", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete named lookup."
          }, 
          "404": {
            "summary": "Named lookup does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete the named lookup definition.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "transforms", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view named lookup."
          }, 
          "404": {
            "summary": "Named lookup does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List a single lookup definition.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "transforms", 
        "params": {
          "default_match": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($disabled$), \"Value of argument 'disabled' must be a boolean\")"
          }, 
          "external_cmd": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "fields_list": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "filename": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "max_matches": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "max_offset_secs": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "min_matches": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "min_offset_secs": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "time_field": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "time_format": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_time_format($time_format$), \"Value of argument 'time_format' must be a time format string\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit named lookup."
          }, 
          "404": {
            "summary": "Named lookup does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Modify the named lookup definition.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "deployment/client": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view deployment client status."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the status of the deployment client in this Splunk instance, including the host/port of its deployment server, and which server classes it is a part of.\n\nA deployment client is a Splunk instance remotely configured by a deployment server. A Splunk instance can be both a deployment server and client at the same time. A Splunk deployment client belongs to one or more server classes.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to deployment client configuration and status."
  }, 
  "deployment/client/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view deployment client."
          }, 
          "404": {
            "summary": "Deployment client does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the configuration for the named deployment client.  The only valid name here is \"deployment-client\".  This is identical to accessing deployment/client without specifying a name.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, disables this deployment client.", 
            "validation": ""
          }, 
          "targetUri": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "URI of the deployment server for this deployment client.\n\nInclude the management port the server is listening on. For example:\n\n<code>deployment_server_uri:mgmtPort</code>\n\nThe default management port is 8089.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit deployment client."
          }, 
          "404": {
            "summary": "Deployment client does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the configuration for this deployment client.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "deployment/client/{name}/reload": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deployment client restarted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to restart deployment client."
          }, 
          "404": {
            "summary": "Deployment client does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Restarts the deployment client, reloading configuration from disk.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "deployment/server": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view all deployment server configurations."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the configurations of all deployment servers.\n\nA deployment server is a Splunk instance that acts as a centralized configuration manager.\nDeployment clients poll server periodically to retrieve configurations.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the configurations of all deployment servers."
  }, 
  "deployment/server/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view this deployment server configuration."
          }, 
          "404": {
            "summary": "Requested deployment server does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Get the configuration information for this deployment server.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "check-new": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, this deployment server reviews the information in its configuration to find out if there is something new or updated to push out to a deployment client.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, disables this deployment server.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit this deployment server configuration."
          }, 
          "404": {
            "summary": "Requested deployment server does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates deployment server instance configuration", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "deployment/serverclass": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view deployment server classes."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists all server classes defined for a deployment server.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "blacklist": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "used to blacklist hosts for this serverclass", 
            "validation": ""
          }, 
          "blacklist.": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "used to blacklist hosts for this serverclass", 
            "validation": ""
          }, 
          "blacklist.0": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.1": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.2": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.3": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.4": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.5": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.6": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.7": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.8": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "blacklist.9": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to disallow this server class", 
            "validation": ""
          }, 
          "continueMatching": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": " Controls how configuration is layered across classes and server-specific settings.\n\nIf true, configuration lookups continue matching server classes, beyond the first match. If false, only the first match is used. Matching is done in the order that server classes are defined. Defaults to true.\n\nA serverClass can override this property and stop the matching.\n", 
            "validation": ""
          }, 
          "endpoint": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a URL template string, which specifies the endpoint from which content can be downloaded by a deployment client. The deployment client knows how to substitute the values of the variables in the URL. Any custom URL can also be supplied here as long as it uses the specified variables.\n\nThis attribute does not need to be specified unless you have a very specific need, for example: to acquire deployment application files from a third-party httpd, for extremely large environments.\n\nCan be overridden at the serverClass level.\n\nDefaults to $deploymentServerUri$/services/streams/deployment?name=$serverClassName$:$appName$", 
            "validation": ""
          }, 
          "filterType": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (whitelist &#124; blacklist)\n\nDetermines the order of execution of filters. If filterType is whitelist, all whitelist filters are applied first, followed by blacklist filters. If filterType is blacklist, all blacklist filters are applied first, followed by whitelist filters.\n\nThe whitelist setting indicates a filtering strategy that pulls in a subset:\n\n* Items are not considered to match the server class  by default.\n* Items that match any whitelist entry, and do not match any blacklist entry, are considered to match the server class.\n* Items that match any blacklist entry are not considered to match the server class, regardless of whitelist.\n\nThe blacklist setting indicates a filtering strategy that rules out a subset:\n\n* Items are considered to match the server class by default.\n* Items that match any blacklist entry, and do not match any whitelist entry, are considered to not match the server class.\n* Items that match any whitelist entry are considered to match the server class.\n\nMore briefly:\n\nwhitelist: default no-match -> whitelists enable -> blacklists disable<br>\nblacklist: default match -> blacklists disable-> whitelists enable\n\nYou can override this value at the serverClass and serverClass:app levels. If you specify whitelist at the global level, and then specify blacklist for an individual server class, the setting becomes blacklist for that server class, and you have to provide another filter in that server class definition to replace the one you overrode.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the server class.", 
            "validation": ""
          }, 
          "repositoryLocation": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The location on the deployment server to store the content that is to be deployed for this server class.\n\nFor example: $SPLUNK_HOME/etc/deployment-apps", 
            "validation": ""
          }, 
          "targetRepositoryLocation": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The location on the deployment client where the content to be deployed for this server class should be installed. \n\nYou can override this in deploymentclient.conf on the deployment client.", 
            "validation": ""
          }, 
          "tmpFolder": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Working folder used by the deployment server.\n\nDefaults to $SPLUNK_HOME@OsDirSep@var@OsDirSep@run@OsDirSep@tmp", 
            "validation": ""
          }, 
          "whitelist": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "list of hosts to accept for this serverclass", 
            "validation": ""
          }, 
          "whitelist.": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "list of hosts to accept for this serverclass", 
            "validation": ""
          }, 
          "whitelist.0": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.1": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.2": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.3": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.4": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.5": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.6": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.7": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.8": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }, 
          "whitelist.9": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Criteria used to identify deployment clients to allow access to this server class", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create a deployment server class."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a server class.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the configuration of a server class.\n\nA server class defines a deployment configuration shared by a group of deployment clients. It defines both the criteria for being a member of the class and the set of content to deploy to members of the class. This content (encapsulated as \"deployment apps\") can consist of Splunk apps, Splunk configurations, and other related content, such as scripts, images, and supporting material. You can define different server classes to reflect the different requirements, OSes, machine types, or functions of your deployment clients."
  }, 
  "deployment/serverclass/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view deployment server class."
          }, 
          "404": {
            "summary": "Deployment server class does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information about this server class.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "blacklist": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.0": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.1": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.2": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.3": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.4": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.5": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.6": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.7": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.8": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "blacklist.9": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "continueMatching": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "endpoint": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "filterType": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "repositoryLocation": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "targetRepositoryLocation": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "tmpFolder": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.0": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.1": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.2": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.3": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.4": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.5": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.6": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.7": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.8": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "whitelist.9": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit deployment server class."
          }, 
          "404": {
            "summary": "Deployment server class does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a new server class.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "deployment/tenants": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view deployment tenants configuration."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists the multi-tenants configuration for this Splunk instance.\n\nMulti-tenants configuration is a type of deployment server topology where more than one deployment server is running on the same Splunk instance, and each of those deployment servers serves content to its own set of deployment clients.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the multi-tenants configuration for this Splunk instance."
  }, 
  "deployment/tenants/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view the deployment tenants configuration."
          }, 
          "404": {
            "summary": "Deployment tenants configuration does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists the configuration for this deployment server in a multi-tenant configuration.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "check-new": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, this deployment server in a multi-tenant configuration reviews the information in its configuration to find out if there is something new or updated to push out to a deployment client.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, disables this deployment server, which is in a multi-tenant configuration.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit the deployment tenants configuration."
          }, 
          "404": {
            "summary": "Deployment tenants configuration does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the configuration for this deployment server in a multi-tenant configuration.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "directory": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view user configurable objects."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Provides an enumeration of the following app scoped objects:\n\n* event types\n* saved searches\n* time configurations\n* views\n* navs\n* manager XML\n* quickstart XML\n* search commands\n* macros\n* tags\n* field extractions\n* lookups\n* workflow actions\n* field aliases\n* sourcetype renames\n\nThis is useful to see which apps provide which objects, or all the objects provided by a specific app. To change the visibility of an object type in this listing, use the showInDirSvc in <code>restmap.conf</code>.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to user configurable objects.\n\nThese objects includes search commands, UI views, UI navigation, saved searches and event types. This is useful to see which objects are provided by all apps, or a specific app when the call is namespaced. The specific configuration in restmap.conf is <code>showInDirSvc</code>.\n\n'''Note:''' This endpoint is new for Splunk 4.3. It replaces the deprecated endpoint accessible from <code>/admin/directory</code>."
  }, 
  "directory/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view the user configurable object."
          }, 
          "404": {
            "summary": "User configurable object does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Displays information about a single entity in the directory service enumeration.\n\nThis is rarely used. Typically after using the directory service enumeration, a client follows the specific link for an object in an enumeration.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "indexing/preview": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }
        }, 
        "summary": "Return a list of all data preview jobs. Data returned includes the Splunk management URI to access each preview job.\n\nUse the data preview job ID as the search_id parameter in [[Documentation:Splunk:RESTAPI:RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fresults_preview|GET /search/jobs/{search_id}/results_preview]] to preview events from the source file.\n\n'''Note: ''' Use the POST operation of this endpoint to create a data preview job and return the corresponding data preview job ID.", 
        "urlParams": {}
      }, 
      "POST": {
        "params": {
          "input.path": {
            "datatype": "String", 
            "default": "", 
            "required": "True", 
            "summary": "The absolute file path to a local file that you want to preview data returned from indexing.", 
            "validation": ""
          }, 
          "props.&lt;props_attr&gt;": {
            "datatype": "String", 
            "default": "", 
            "required": "False", 
            "summary": "Define a new sourcetype in props.conf for preview data that you are indexing.\n\nTypically, you first examine preveiw data events returned from GET /search/jobs/{job_id}events. Then you define new sourcetypes as needed with this endpoint.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }
        }, 
        "summary": "Create a preview data job for the specified source file, returning the preview data job ID. Use the preview job ID as the search_id parameter in [[Documentation:Splunk:RESTAPI:RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fresults_preview|GET /search/jobs/{search_id}/results_preview]] to obtain a data preview.\n\nYou can optionally define sourcetypes for preview data job in props.conf.", 
        "urlParams": {}
      }
    }, 
    "summary": "Preview events from a source file before you index the file.\n\nTypically, you create a data preview job for a source file. Use the resulting data preview job ID as the search_id parameter in [[Documentation:Splunk:RESTAPI:RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fresults_preview|GET /search/jobs/{search_id}/results_preview]] to preview events that would be generated from indexing the source file.\n\nYou can also check the status of a data preview job with GET /search/jobs/{search_id} to obtain information such as the dispatchState, doneProgress, and eventCount. For more information, see [[Documentation:Splunk:RESTAPI:RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D|GET /search/jobs/{search_id}]].\n\n'''Note:''' This endpoint is new in Splunk 4.3."
  }, 
  "indexing/preview/{job_id}": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "404": {
            "summary": "Specified job ID does not exist."
          }
        }, 
        "summary": "Returns the props.conf settings for the data preview job specified by {job_id}.", 
        "urlParams": {
          "job_id": {
            "required": "true", 
            "summary": "job_id"
          }
        }
      }
    }
  }, 
  "licenser/groups": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view licenser groups."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists all licenser groups.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the configuration of licenser groups.\n\nA licenser group contains one or more licenser stacks that can operate concurrently.  Only one licenser group is active at any given time"
  }, 
  "licenser/groups/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view licenser groups."
          }, 
          "404": {
            "summary": "Licenser groups does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists a specific licenser group.  A licenser group contains one or more licenser stacks that can operate concurrently.  Only one licenser group is active at any given time", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "is_active": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "true", 
            "summary": "Active specific licenser group", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit licenser group."
          }, 
          "404": {
            "summary": "Licenser group does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Activates specific licenser group with the side effect of deactivating the previously active one.\n\nThere can only be a single active licenser group for a given instance of Splunk.  Use this to switch between, for example, free to enterprise, or download-trial to free.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "licenser/licenses": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view licenses."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists all licenses that have been added.  Only a subset of these licenses may be active however, this is simply listing all licenses in every stack/group, regardless of which group is active", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "name": {
            "datatype": "string", 
            "default": "", 
            "required": "true", 
            "summary": "Path to license file on server. If the payload parameter is specified, the name parameter is ignored.", 
            "validation": ""
          }, 
          "payload": {
            "datatype": "string", 
            "default": "", 
            "required": "false", 
            "summary": "String representation of license, encoded in xml", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to add a license."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Add a license entitlement to this instance.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the licenses for this Splunk instance.\n\nA license enables various features for a splunk instance, including but not limitted to indexing quota, auth, search, forwarding, and so forth."
  }, 
  "licenser/licenses/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete license."
          }, 
          "404": {
            "summary": "License does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete the license with hash corresponding to {name}.\n\nNOTE: You cannot delete the last license out of an active group. First, deactivate the group (by switching to another group) and then perform the delete.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view license."
          }, 
          "404": {
            "summary": "License does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List attributes of specific license.  The {name} portion of URL is actually the hash of the license payload.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "licenser/messages": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view licenser messages."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists all messages/alerts/persisted warnings for this node.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to licenser messages.\n\nMessages may range from helpful warnings about being close to violations, licenses expiring or more severe alerts regarding overages and exceeding license warning window."
  }, 
  "licenser/messages/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view licenser messages."
          }, 
          "404": {
            "summary": "Licenser message does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List specific message whose msgId corresponds to {name} component.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "licenser/pools": {
    "methods": {
      "GET": {
        "config": "server", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view licenser pools."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Enumerates all pools.  A pool logically partitions the daily volume entitlements of a stack. You can use a pool to divide license privileges amongst multiple slaves", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "server", 
        "params": {
          "description": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "description of this pool", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Edit the properties of the specified pool", 
            "validation": ""
          }, 
          "quota": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Defines the byte quota of this pool.\n\nValid values:\n\nMAX: maximum amount allowed by the license. You can only have one pool with MAX size in a stack.\n\nNumber[MB&#124;GB]: Specify a specific size. For example, 552428800, or simply specify 50MB.", 
            "validation": ""
          }, 
          "slaves": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Comma-separated list of slaveids that are members of this pool, or '*' to accept all slaves.\n\nYou can also specify a comma-separated list guids to specify slaves that can connect to this pool.", 
            "validation": ""
          }, 
          "stack_id": {
            "datatype": "Enum", 
            "default": "", 
            "required": "true", 
            "summary": "Valid values: (download-trial &#124; enterprise &#124; forwarder &#124; free)\n\nStack ID of the stack corresponding to this pool", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create licenser pools."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a license pool.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the licenser pools configuration.\n\nA pool logically partitions the daily volume entitlements of a stack. You can use a license pool to divide license privileges amongst multiple slaves"
  }, 
  "licenser/pools/{name}": {
    "methods": {
      "DELETE": {
        "config": "server", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete licenser pool."
          }, 
          "404": {
            "summary": "Licenser pool does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete specified pool.  Deleting pools is not supported for every pool. Certain stacks have fixed pools which cannot be deleted.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "server", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view licenser pools."
          }, 
          "404": {
            "summary": "Licenser pool does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists details of the pool specified by {name}.\n\nA pool logically partitions the daily volume entitlements of a stack. A pool can be used to divide license privileges amongst multiple slaves", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "server", 
        "params": {
          "append_slaves": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Flag which controls whether newly specified slaves will be appended to existing slaves list or overwritten", 
            "validation": ""
          }, 
          "description": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "quota": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "slaves": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit licenser pool."
          }, 
          "404": {
            "summary": "Licenser pool does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Edit properties of the pool specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "licenser/slaves": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "poolid": {
            "datatype": "n/a", 
            "default": "", 
            "required": "false", 
            "summary": "Do not use.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }, 
          "stackid": {
            "datatype": "string", 
            "default": "", 
            "required": "false", 
            "summary": "Do not use.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view license slaves."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List all slaves registered to this license master.  Any slave that attempts to connect to master is reported, regardless of whether it is allocated to a master licenser pool.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to slaves reporting to this license master."
  }, 
  "licenser/slaves/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "poolid": {
            "datatype": "Do not use.", 
            "default": "", 
            "required": "false", 
            "summary": "Do not use.", 
            "validation": ""
          }, 
          "stackid": {
            "datatype": "string", 
            "default": "", 
            "required": "false", 
            "summary": "do not use", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view license slave."
          }, 
          "404": {
            "summary": "License slave does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List attributes of slave specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "licenser/stacks": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view license stacks."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Enumerate all license stacks.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the license stack configuration.\n\nA license stack is comprised of one or more licenses of the same \"type\".  The daily indexing quota of a license stack is additive, so a stack represents the aggregate entitlement for a collection of licenses."
  }, 
  "licenser/stacks/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view license stacks."
          }, 
          "404": {
            "summary": "License stack does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Retrieve details of specific license stacks.  A license stack is comprised of one or more licenses of the same \"type\".  The daily indexing quota of a license stack is additive, so a stack represents the aggregate entitlement for a collection of licenses.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "messages": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view messages."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Enumerate all systemwide messages. This is typically used for splunkd to advertise issues such as license quotas, license expirations, misconfigured indexes, and disk space.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The primary key of this message.", 
            "validation": ""
          }, 
          "value": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The text of the message.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create message."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create a persistent message displayed at /services/messages.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to Splunk system messages. Most messages are created by splunkd to inform the user of system problems.\n\nSplunk Web typically displays these as bulletin board messages."
  }, 
  "messages/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete message."
          }, 
          "404": {
            "summary": "Message does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes a message identified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view message."
          }, 
          "404": {
            "summary": "Message does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Get the entry corresponding of a single message identified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "properties": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }
        }, 
        "summary": "Returns a list of configurations that are saved in configuration files.", 
        "urlParams": {}
      }, 
      "POST": {
        "params": {
          "__conf": {
            "datatype": "String", 
            "default": "", 
            "required": "True", 
            "summary": "The name of the configuration file to create.\n\n<b>Note</b>: Double underscore before conf.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }
        }, 
        "summary": "Creates a new configuration file.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to configuration files.\n\nRefer to [[Documentation:Splunk:RESTAPI:RESTconfigurations|Accessing and updating Splunk configurations]] for a comparison of these endpoints with the <code>configs/conf-{file}</code> endpoints.\n\n'''Note: ''' The DELETE operation from the <code>properties</code> endpoint is deprecated and will be removed from future releases. Instead, use the DELETE operation from the [[Documentation:Splunk:RESTAPI:RESTconfig#DELETE_configs.2Fconf-.7Bfile.7D.2F.7Bname.7D|configs/conf-{file}/{name} endpoint]]."
  }, 
  "properties/{file_name}": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "404": {
            "summary": "Named file does not exist."
          }
        }, 
        "summary": "Returns a list of stanzas in the configuration file specified by {name}.", 
        "urlParams": {
          "file_name": {
            "required": "true", 
            "summary": "file_name"
          }
        }
      }, 
      "POST": {
        "params": {
          "__stanza": {
            "datatype": "String", 
            "default": "", 
            "required": "True", 
            "summary": "The name of the stanza to create.\n\n<b>Note</b>: Double underscore before stanza.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Stanza created successfully."
          }, 
          "303": {
            "summary": "Stanza already exists."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }
        }, 
        "summary": "Creates a new stanza in the configuratin file specified by {name}.", 
        "urlParams": {
          "file_name": {
            "required": "true", 
            "summary": "file_name"
          }
        }
      }
    }
  }, 
  "properties/{file_name}/{stanza_name}": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "404": {
            "summary": "Stanza does not exist."
          }
        }, 
        "summary": "Returns the configuration values for the stanza represented by {stanza_name} in the configuration file specified by {file_name}.", 
        "urlParams": {
          "file_name": {
            "required": "true", 
            "summary": "file_name"
          }, 
          "stanza_name": {
            "required": "true", 
            "summary": "stanza_name"
          }
        }
      }, 
      "POST": {
        "params": {
          "&lt;key_name&gt;": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Specifies a key/value pair to update.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "404": {
            "summary": "Stanza does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See returned XML for explanation."
          }
        }, 
        "summary": "Adds or updates key/value pairs in the specified stanza. One or more key/value pairs may be passed at one time to this endpoint.", 
        "urlParams": {
          "file_name": {
            "required": "true", 
            "summary": "file_name"
          }, 
          "stanza_name": {
            "required": "true", 
            "summary": "stanza_name"
          }
        }
      }
    }
  }, 
  "properties/{file_name}/{stanza_name}/{key_name}": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "404": {
            "summary": "Key in the stanza does not exist."
          }
        }, 
        "summary": "Returns the value of the key in plain text for specified stanza and configuration file.", 
        "urlParams": {
          "file_name": {
            "required": "true", 
            "summary": "file_name"
          }, 
          "key_name": {
            "required": "true", 
            "summary": "key_name"
          }, 
          "stanza_name": {
            "required": "true", 
            "summary": "stanza_name"
          }
        }
      }, 
      "POST": {
        "params": {
          "value": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The value to set for the named key in this named stanza in the named configuration file.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "404": {
            "summary": "Key does not exist in the stanza."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See returned XML for explanation."
          }
        }, 
        "summary": "Update an existing key value.", 
        "urlParams": {
          "file_name": {
            "required": "true", 
            "summary": "file_name"
          }, 
          "key_name": {
            "required": "true", 
            "summary": "key_name"
          }, 
          "stanza_name": {
            "required": "true", 
            "summary": "stanza_name"
          }
        }
      }
    }
  }, 
  "receivers/simple": {
    "methods": {
      "POST": {
        "params": {
          "&lt;arbitrary_data&gt;": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Raw event text.  This will be the entirety of the HTTP request body.", 
            "validation": ""
          }, 
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value to populate in the host field for events from this data input.", 
            "validation": ""
          }, 
          "host_regex": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A regular expression used to extract the host value from each event.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "default", 
            "required": "false", 
            "summary": "The index to send events from this input to.", 
            "validation": ""
          }, 
          "source": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The source value to fill in the metadata for this input's events.", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The sourcetype to apply to events from this input.", 
            "validation": ""
          }
        }, 
        "request": "Note that all metadata is specified via GET parameters.", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Data accepted."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "404": {
            "summary": "Receiver does not exist."
          }
        }, 
        "summary": "Create events from the contents contained in the HTTP body.", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for sending events to Splunk in an HTTP request."
  }, 
  "receivers/stream": {
    "methods": {
      "POST": {
        "params": {
          "&lt;data_stream&gt;": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Raw event text.  This does not need to be presented as a complete HTTP request, but can be streamed in as data is available.", 
            "validation": ""
          }, 
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The value to populate in the host field for events from this data input.", 
            "validation": ""
          }, 
          "host_regex": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A regular expression used to extract the host value from each event.", 
            "validation": ""
          }, 
          "index": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The index to send events from this input to.", 
            "validation": ""
          }, 
          "source": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The source value to fill in the metadata for this input's events.", 
            "validation": ""
          }, 
          "sourcetype": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The sourcetype to apply to events from this input.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Data accepted."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "404": {
            "summary": "Receiver does not exist."
          }
        }, 
        "summary": "Create events from the stream of data following HTTP headers.", 
        "urlParams": {}
      }
    }, 
    "summary": "Opens a socket for streaming events to Splunk."
  }, 
  "saved/eventtypes": {
    "methods": {
      "GET": {
        "config": "eventtypes", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view event types."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Retrieve saved event types.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "eventtypes", 
        "params": {
          "description": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Human-readable description of this event type.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "If True, disables the event type.", 
            "validation": ""
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name for the event type.", 
            "validation": ""
          }, 
          "priority": {
            "datatype": "Number", 
            "default": "1", 
            "required": "false", 
            "summary": "Specify an integer from 1 to 10 for the value used to determine the order in which the matching event types of an event are displayed. 1 is the highest priority.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Search terms for this event type.", 
            "validation": ""
          }, 
          "tags": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Deprecated. Use tags.conf.spec file to assign tags to groups of events with related field values.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create an event type."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a new event type.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to saved event types."
  }, 
  "saved/eventtypes/{name}": {
    "methods": {
      "DELETE": {
        "config": "eventtypes", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete event type."
          }, 
          "404": {
            "summary": "Event type does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes this event type.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "eventtypes", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view event type."
          }, 
          "404": {
            "summary": "Event type does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information on this event type.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "eventtypes", 
        "params": {
          "description": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "priority": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "search": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "tags": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit event type."
          }, 
          "404": {
            "summary": "Event type does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates this event type.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "saved/searches": {
    "methods": {
      "GET": {
        "config": "savedsearches", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "earliest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "For scheduled searches display all the scheduled times starting from this time (not just the next run time)", 
            "validation": ""
          }, 
          "latest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "For scheduled searches display all the scheduled times until this time (not just the next run time)", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view saved search."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information on all saved searches.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "savedsearches", 
        "params": {
          "action.*": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Wildcard argument that accepts any action.", 
            "validation": ""
          }, 
          "action.email": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "The state of the email action. Read-only attribute. Value ignored on POST. Use actions to specify a list of enabled actions.", 
            "validation": ""
          }, 
          "action.email.auth_password": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The password to use when authenticating with the SMTP server. Normally this value will be set when editing the email settings, however you can set a clear text password here and it will be encrypted on the next Splunk restart.\n\nDefaults to empty string.", 
            "validation": ""
          }, 
          "action.email.auth_username": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The username to use when authenticating with the SMTP server. If this is empty string, no authentication is attempted. Defaults to empty string.\n\nNOTE: Your SMTP server might reject unauthenticated emails.", 
            "validation": ""
          }, 
          "action.email.bcc": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "BCC email address to use if action.email is enabled. ", 
            "validation": ""
          }, 
          "action.email.cc": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "CC email address to use if action.email is enabled.", 
            "validation": ""
          }, 
          "action.email.command": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The search command (or pipeline) which is responsible for executing the action.\n\nGenerally the command is a template search pipeline which is realized with values from the saved search. To reference saved search field values wrap them in $, for example to reference the savedsearch name use $name$, to reference the search use $search$.", 
            "validation": ""
          }, 
          "action.email.format": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (plain &#124; html &#124; raw &#124; csv)\n\nSpecify the format of text in the email. This value also applies to any attachments.", 
            "validation": ""
          }, 
          "action.email.from": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Email address from which the email action originates.\n\nDefaults to splunk@$LOCALHOST or whatever value is set in alert_actions.conf.", 
            "validation": ""
          }, 
          "action.email.hostname": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the hostname used in the web link (url) sent in email actions.\n\nThis value accepts two forms:\n\nhostname (for example, splunkserver, splunkserver.example.com)\n\nprotocol://hostname:port (for example, http://splunkserver:8000, https://splunkserver.example.com:443)\n\nWhen this value is a simple hostname, the protocol and port which are configured within splunk are used to construct the base of the url.\n\nWhen this value begins with 'http://', it is used verbatim. NOTE: This means the correct port must be specified if it is not the default port for http or https. This is useful in cases when the Splunk server is not aware of how to construct an externally referencable url, such as SSO environments, other proxies, or when the Splunk server hostname is not generally resolvable.\n\nDefaults to current hostname provided by the operating system, or if that fails \"localhost\". When set to empty, default behavior is used.", 
            "validation": ""
          }, 
          "action.email.inline": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the search results are contained in the body of the email.\n\nResults can be either inline or attached to an email. See action.email.sendresults.", 
            "validation": ""
          }, 
          "action.email.mailserver": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Set the address of the MTA server to be used to send the emails.\n\nDefaults to <LOCALHOST> (or whatever is set in alert_actions.conf).", 
            "validation": ""
          }, 
          "action.email.maxresults": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the global maximum number of search results to send when email.action is enabled.\n\nDefaults to 100.", 
            "validation": ""
          }, 
          "action.email.maxtime": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are Integer&#91;m&#124;s&#124;h&#124;d&#93;.\n\nSpecifies the maximum amount of time the execution of an email action takes before the action is aborted. Defaults to 5m.", 
            "validation": ""
          }, 
          "action.email.pdfview": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The name of the view to deliver if sendpdf is enabled", 
            "validation": ""
          }, 
          "action.email.preprocess_results": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search string to preprocess results before emailing them. Defaults to empty string (no preprocessing).\n\nUsually the preprocessing consists of filtering out unwanted internal fields.", 
            "validation": ""
          }, 
          "action.email.reportPaperOrientation": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (portrait &#124; landscape)\n\nSpecifies the paper orientation: portrait or landscape. Defaults to portrait.", 
            "validation": ""
          }, 
          "action.email.reportPaperSize": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (letter &#124; legal &#124; ledger &#124; a2 &#124; a3 &#124; a4 &#124; a5)\n\nSpecifies the paper size for PDFs. Defaults to letter.", 
            "validation": ""
          }, 
          "action.email.reportServerEnabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the PDF server is enabled. Defaults to false.", 
            "validation": ""
          }, 
          "action.email.reportServerURL": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": " The URL of the PDF report server, if one is set up and available on the network.\n\nFor a default locally installed report server, the URL is http://localhost:8091/", 
            "validation": ""
          }, 
          "action.email.sendpdf": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether to create and send the results as a PDF. Defaults to false.", 
            "validation": ""
          }, 
          "action.email.sendresults": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether to attach the search results in the email.\n\nResults can be either attached or inline. See action.email.inline. ", 
            "validation": ""
          }, 
          "action.email.subject": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies an alternate email subject.\n\nDefaults to SplunkAlert-<savedsearchname>.", 
            "validation": ""
          }, 
          "action.email.to": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A comma or semicolon separated list of recipient email addresses. Required if this search is scheduled and the email alert action is enabled.", 
            "validation": ""
          }, 
          "action.email.track_alert": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the execution of this action signifies a trackable alert.", 
            "validation": ""
          }, 
          "action.email.ttl": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are Integer[p].\n\nSpecifies the minimum time-to-live in seconds of the search artifacts if this action is triggered. If p follows &lt;Integer&gt;, int is the number of scheduled periods. Defaults to 86400 (24 hours).\n\nIf no actions are triggered, the artifacts have their ttl determined by dispatch.ttl in savedsearches.conf.", 
            "validation": ""
          }, 
          "action.email.use_ssl": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether to use SSL when communicating with the SMTP server.\n\nDefaults to false.", 
            "validation": ""
          }, 
          "action.email.use_tls": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether to use TLS (transport layer security) when communicating with the SMTP server (starttls).\n\nDefaults to false.", 
            "validation": ""
          }, 
          "action.email.width_sort_columns": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether columns should be sorted from least wide to mos wide, left to right.\n\nOnly valid if format=text.", 
            "validation": ""
          }, 
          "action.populate_lookup": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "The state of the populate lookup action. Read-only attribute. Value ignored on POST. Use actions to specify a list of enabled actions.", 
            "validation": ""
          }, 
          "action.populate_lookup.command": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The search command (or pipeline) which is responsible for executing the action.\n\nGenerally the command is a template search pipeline which is realized with values from the saved search. To reference saved search field values wrap them in $, for example to reference the savedsearch name use $name$, to reference the search use $search$.", 
            "validation": ""
          }, 
          "action.populate_lookup.dest": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Lookup name of path of the lookup to populate", 
            "validation": ""
          }, 
          "action.populate_lookup.hostname": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the hostname used in the web link (url) sent in alert actions.\n\nThis value accepts two forms:\n\nhostname (for example, splunkserver, splunkserver.example.com)\n\nprotocol://hostname:port (for example, http://splunkserver:8000, https://splunkserver.example.com:443)\n\nSee action.email.hostname for details.", 
            "validation": ""
          }, 
          "action.populate_lookup.maxresults": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the maximum number of search results sent via alerts. Defaults to 100.", 
            "validation": ""
          }, 
          "action.populate_lookup.maxtime": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are: Integer[m&#124;s&#124;h&#124;d]\n\nSets the maximum amount of time the execution of an action takes before the action is aborted. Defaults to 5m.", 
            "validation": ""
          }, 
          "action.populate_lookup.track_alert": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the execution of this action signifies a trackable alert.", 
            "validation": ""
          }, 
          "action.populate_lookup.ttl": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are Integer[p]\n\nSpecifies the minimum time-to-live in seconds of the search artifacts if this action is triggered. If p follows Integer, then this specifies the number of scheduled periods. Defaults to 10p.\n\nIf no actions are triggered, the artifacts have their ttl determined by dispatch.ttl in savedsearches.conf.", 
            "validation": ""
          }, 
          "action.rss": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "The state of the rss action. Read-only attribute. Value ignored on POST. Use actions to specify a list of enabled actions.", 
            "validation": ""
          }, 
          "action.rss.command": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The search command (or pipeline) which is responsible for executing the action.\n\nGenerally the command is a template search pipeline which is realized with values from the saved search. To reference saved search field values wrap them in $, for example to reference the savedsearch name use $name$, to reference the search use $search$.", 
            "validation": ""
          }, 
          "action.rss.hostname": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the hostname used in the web link (url) sent in alert actions.\n\nThis value accepts two forms:\n\nhostname (for example, splunkserver, splunkserver.example.com)\n\nprotocol://hostname:port (for example, http://splunkserver:8000, https://splunkserver.example.com:443)\n\nSee action.email.hostname for details.", 
            "validation": ""
          }, 
          "action.rss.maxresults": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the maximum number of search results sent via alerts. Defaults to 100.", 
            "validation": ""
          }, 
          "action.rss.maxtime": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are Integer[m&#124;s&#124;h&#124;d].\n\nSets the maximum amount of time the execution of an action takes before the action is aborted. Defaults to 1m.", 
            "validation": ""
          }, 
          "action.rss.track_alert": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the execution of this action signifies a trackable alert.", 
            "validation": ""
          }, 
          "action.rss.ttl": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are: Integer[p]\n\nSpecifies the minimum time-to-live in seconds of the search artifacts if this action is triggered. If p follows Integer, specifies the number of scheduled periods. Defaults to 86400 (24 hours).\n\nIf no actions are triggered, the artifacts have their ttl determined by dispatch.ttl in savedsearches.conf.", 
            "validation": ""
          }, 
          "action.script": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "The state of the script action. Read-only attribute. Value ignored on POST. Use actions to specify a list of enabled actions.", 
            "validation": ""
          }, 
          "action.script.command": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The search command (or pipeline) which is responsible for executing the action.\n\nGenerally the command is a template search pipeline which is realized with values from the saved search. To reference saved search field values wrap them in $, for example to reference the savedsearch name use $name$, to reference the search use $search$.", 
            "validation": ""
          }, 
          "action.script.filename": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "File name of the script to call. Required if script action is enabled", 
            "validation": ""
          }, 
          "action.script.hostname": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the hostname used in the web link (url) sent in alert actions.\n\nThis value accepts two forms:\n\nhostname (for example, splunkserver, splunkserver.example.com)\n\nprotocol://hostname:port (for example, http://splunkserver:8000, https://splunkserver.example.com:443)\n\nSee action.email.hostname for details.", 
            "validation": ""
          }, 
          "action.script.maxresults": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the maximum number of search results sent via alerts. Defaults to 100.", 
            "validation": ""
          }, 
          "action.script.maxtime": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are: Integer[m&#124;s&#124;h&#124;d]\n\nSets the maximum amount of time the execution of an action takes before the action is aborted. Defaults to 5m.", 
            "validation": ""
          }, 
          "action.script.track_alert": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the execution of this action signifies a trackable alert.", 
            "validation": ""
          }, 
          "action.script.ttl": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are: Integer[p]\n\nSpecifies the minimum time-to-live in seconds of the search artifacts if this action is triggered. If p follows Integer, specifies the number of scheduled periods. Defaults to 600 (10 minutes).\n\nIf no actions are triggered, the artifacts have their ttl determined by dispatch.ttl in savedsearches.conf.", 
            "validation": ""
          }, 
          "action.summary_index": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "The state of the summary index action. Read-only attribute. Value ignored on POST. Use actions to specify a list of enabled actions.\n\nDefaults to 0", 
            "validation": ""
          }, 
          "action.summary_index._name": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies the name of the summary index where the results of the scheduled search are saved.\n\nDefaults to \"summary.\"", 
            "validation": ""
          }, 
          "action.summary_index.command": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The search command (or pipeline) which is responsible for executing the action.\n\nGenerally the command is a template search pipeline which is realized with values from the saved search. To reference saved search field values wrap them in $, for example to reference the savedsearch name use $name$, to reference the search use $search$.", 
            "validation": ""
          }, 
          "action.summary_index.hostname": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the hostname used in the web link (url) sent in alert actions.\n\nThis value accepts two forms:\n\nhostname (for example, splunkserver, splunkserver.example.com)\n\nprotocol://hostname:port (for example, http://splunkserver:8000, https://splunkserver.example.com:443)\n\nSee action.email.hostname for details.", 
            "validation": ""
          }, 
          "action.summary_index.inline": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Determines whether to execute the summary indexing action as part of the scheduled search. \n\n<b>NOTE:</b> This option is considered only if the summary index action is enabled and is always executed (in other words, if <code>counttype = always</code>).\n\nDefaults to true", 
            "validation": ""
          }, 
          "action.summary_index.maxresults": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Sets the maximum number of search results sent via alerts. Defaults to 100.", 
            "validation": ""
          }, 
          "action.summary_index.maxtime": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are: Integer[m&#124;s&#124;h&#124;d]\n\nSets the maximum amount of time the execution of an action takes before the action is aborted. Defaults to 5m.", 
            "validation": ""
          }, 
          "action.summary_index.track_alert": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether the execution of this action signifies a trackable alert.", 
            "validation": ""
          }, 
          "action.summary_index.ttl": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values are: Integer[p]\n\nSpecifies the minimum time-to-live in seconds of the search artifacts if this action is triggered. If p follows Integer, specifies the number of scheduled periods. Defaults to 10p.\n\nIf no actions are triggered, the artifacts have their ttl determined by dispatch.ttl in savedsearches.conf.", 
            "validation": ""
          }, 
          "actions": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "List of enabled actions", 
            "validation": ""
          }, 
          "alert.digest_mode": {
            "datatype": "Boolean", 
            "default": "1", 
            "required": "false", 
            "summary": "Specifies whether Splunk applies the alert actions to the entire result set or on each individual result.\n\nDefaults to true.\n", 
            "validation": ""
          }, 
          "alert.expires": {
            "datatype": "Number", 
            "default": "24h", 
            "required": "false", 
            "summary": "Valid values: [number][time-unit]\n\nSets the period of time to show the alert in the dashboard. Defaults to 24h.\n\nUse [number][time-unit] to specify a time. For example: 60 = 60 seconds, 1m = 1 minute, 1h = 60 minutes = 1 hour.", 
            "validation": ""
          }, 
          "alert.severity": {
            "datatype": "Enum", 
            "default": "3", 
            "required": "false", 
            "summary": "Valid values: (1 &#124; 2 &#124; 3 &#124; 4 &#124; 5 &#124; 6)\n\nSets the alert severity level.\n\nValid values are:\n\n1 DEBUG\n2 INFO\n3 WARN\n4 ERROR\n5 SEVERE\n6 FATAL", 
            "validation": ""
          }, 
          "alert.suppress": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "Indicates whether alert suppression is enabled for this schedules search.", 
            "validation": ""
          }, 
          "alert.suppress.fields": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Comma delimited list of fields to use for suppression when doing per result alerting. Required if suppression is turned on and per result alerting is enabled.", 
            "validation": ""
          }, 
          "alert.suppress.period": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: [number][time-unit]\n\nSpecifies the suppresion period. Only valid if <code>alert.supress</code> is enabled.\n\nUse [number][time-unit] to specify a time. For example: 60 = 60 seconds, 1m = 1 minute, 1h = 60 minutes = 1 hour.", 
            "validation": ""
          }, 
          "alert.track": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (true &#124; false &#124; auto)\n\nSpecifies whether to track the actions triggered by this scheduled search.\n\nauto  - determine whether to track or not based on the tracking setting of each action, do not track scheduled searches that always trigger actions.\n\ntrue  - force alert tracking.\n\nfalse - disable alert tracking for this search.\n", 
            "validation": ""
          }, 
          "alert_comparator": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "One of the following strings: greater than, less than, equal to, rises by, drops by, rises by perc, drops by perc", 
            "validation": ""
          }, 
          "alert_condition": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Contains a conditional search that is evaluated against the results of the saved search. Defaults to an empty string.\n\nAlerts are triggered if the specified search yields a non-empty search result list.\n\nNOTE: If you specify an alert_condition, do not set counttype, relation, or quantity.\n", 
            "validation": ""
          }, 
          "alert_threshold": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "The value to compare to before triggering the alert actions. Valid values are: Integer[%]?", 
            "validation": ""
          }, 
          "alert_type": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "What to base the alert on, overriden by alert_condition if it is specified. Valid values are: always, custom, number of events, number of hosts, number of sources ", 
            "validation": ""
          }, 
          "args.*": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Wildcard argument that accepts any saved search template argument, such as args.username=foobar when the search is search $username$.", 
            "validation": ""
          }, 
          "cron_schedule": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: cron string\n\nThe cron schedule to execute this search. For example: */5 * * * *  causes the search to execute every 5 minutes.\n\ncron lets you use standard cron notation to define your scheduled search interval. In particular, cron can accept this type of notation: 00,20,40 * * * *, which runs the search every hour at hh:00, hh:20, hh:40. Along the same lines, a cron of 03,23,43 * * * * runs the search every hour at hh:03, hh:23, hh:43.\n\nSplunk recommends that you schedule your searches so that they are staggered over time. This  reduces system load. Running all of them every 20 minutes (*/20) means they would all launch at hh:00 (20, 40) and might slow your system every 20 minutes.", 
            "validation": ""
          }, 
          "description": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Human-readable description of this saved search. Defaults to empty string.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "Indicates if the saved search is enabled.\n\nDisabled saved searches are not visible in Splunk Web.", 
            "validation": ""
          }, 
          "dispatch.*": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Wildcard argument that accepts any dispatch related argument.", 
            "validation": ""
          }, 
          "dispatch.buckets": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "The maximum nuber of timeline buckets.", 
            "validation": "validate(isint($dispatch.buckets$) AND $dispatch.buckets$>=0, \"Value of argument 'dispatch.buckets' must be a non-negative integer\")"
          }, 
          "dispatch.earliest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A time string that specifies the earliest time for this search. Can be a relative or absolute time.\n\nIf this value is an absolute time, use the dispatch.time_format to format the value.", 
            "validation": ""
          }, 
          "dispatch.latest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A time string that specifies the latest time for this saved search. Can be a relative or absolute time.\n\nIf this value is an absolute time, use the dispatch.time_format to format the value.", 
            "validation": ""
          }, 
          "dispatch.lookups": {
            "datatype": "Boolean", 
            "default": "1", 
            "required": "false", 
            "summary": "Enables or disables the lookups for this search.", 
            "validation": "validate(is_bool($dispatch.lookups$), \"Value of argument 'dispatch.lookups' must be a boolean\")"
          }, 
          "dispatch.max_count": {
            "datatype": "Number", 
            "default": "500000", 
            "required": "false", 
            "summary": "The maximum number of results before finalizing the search.", 
            "validation": "validate(isint($dispatch.max_count$) AND $dispatch.max_count$>=0, \"Value of argument 'dispatch.max_count' must be a non-negative integer\")"
          }, 
          "dispatch.max_time": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Indicates the maximum amount of time (in seconds) before finalizing the search.", 
            "validation": ""
          }, 
          "dispatch.reduce_freq": {
            "datatype": "Number", 
            "default": "10", 
            "required": "false", 
            "summary": "Specifies how frequently Splunk should run the MapReduce reduce phase on accumulated map values.", 
            "validation": ""
          }, 
          "dispatch.rt_backfill": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "Whether to back fill the real time window for this search. Parameter valid only if this is a real time search", 
            "validation": ""
          }, 
          "dispatch.spawn_process": {
            "datatype": "Boolean", 
            "default": "1", 
            "required": "false", 
            "summary": "Specifies whether Splunk spawns a new search process when this saved search is executed.", 
            "validation": "validate(is_bool($dispatch.spawn_process$), \"Value of argument 'dispatch.spawn_process' must be a boolean\")"
          }, 
          "dispatch.time_format": {
            "datatype": "String", 
            "default": "%FT%T.%Q%:z", 
            "required": "false", 
            "summary": "A time format string that defines the time format that Splunk uses to specify the earliest and latest time.", 
            "validation": "validate(is_time_format($dispatch.time_format$), \"Value of argument 'dispatch.time_format' must be a time format string\")"
          }, 
          "dispatch.ttl": {
            "datatype": "Number", 
            "default": "2p", 
            "required": "false", 
            "summary": "Valid values: Integer[p]<\n\nIndicates the time to live (in seconds) for the artifacts of the scheduled search, if no  actions are triggered.\n\nIf an action is triggered Splunk changes the ttl to that action's ttl. If multiple actions are triggered, Splunk applies the maximum ttl to the artifacts. To set the action's ttl, refer to alert_actions.conf.spec.\n\nIf the integer is followed by the letter 'p' Splunk interprets the ttl as a multiple of the scheduled search's period.", 
            "validation": ""
          }, 
          "displayview": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Defines the default UI view name (not label) in which to load the results. Accessibility is subject to the user having sufficient permissions.", 
            "validation": ""
          }, 
          "is_scheduled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Whether this search is to be ran on a schedule", 
            "validation": "validate(is_bool($is_scheduled$), \"Value of argument 'is_scheduled' must be a boolean\")"
          }, 
          "is_visible": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "Specifies whether this saved search should be listed in the visible saved search list.", 
            "validation": "validate(is_bool($is_visible$), \"Value of argument 'is_visible' must be a boolean\")"
          }, 
          "max_concurrent": {
            "datatype": "Number", 
            "default": "1", 
            "required": "false", 
            "summary": "The maximum number of concurrent instances of this search the scheduler is allowed to run.", 
            "validation": "validate(isint($max_concurrent$) AND $max_concurrent$>=0, \"Value of argument 'max_concurrent' must be a non-negative integer\")"
          }, 
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Use this parameter to specify multiple actions.\n\nFor example, you can specify:\n\ncurl -k -u admin:pass https://localhost:8089/servicesNS/admin/search/saved/searches -d name=MySavedSearch42 --data-urlencode search=\"index=_internal source=*metrics.log\" -d action.email.cc=receiver@example.com&action.email.bcc=receiver@example.com\n", 
            "validation": ""
          }, 
          "next_scheduled_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Read-only attribute. Value ignored on POST. There are some old clients who still send this value", 
            "validation": ""
          }, 
          "qualifiedSearch": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Read-only attribute. Value ignored on POST. Splunk computes this value during runtime.", 
            "validation": ""
          }, 
          "realtime_schedule": {
            "datatype": "Boolean", 
            "default": "1", 
            "required": "false", 
            "summary": "Controls the way the scheduler computes the next execution time of a scheduled search. If this value is set to 1, the scheduler bases its determination of the next scheduled search execution time on the current time.\n\nIf this value is set to 0, the scheduler bases its determination of the next scheduled search on the last search execution time. This is called continuous scheduling. If set to 0, the scheduler never skips scheduled execution periods. However, the execution of the saved search might fall behind depending on the scheduler's load. Use continuous scheduling whenever you enable the summary index option.\n\nIf set to 1, the scheduler might skip some execution periods to make sure that the scheduler is executing the searches running over the most recent time range.\n\nThe scheduler tries to execute searches that have realtime_schedule set to 1 before it executes searches that have continuous scheduling (realtime_schedule = 0).", 
            "validation": "validate(is_bool($realtime_schedule$), \"Value of argument 'realtime_schedule' must be a boolean\")"
          }, 
          "request.ui_dispatch_app": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies a field used by Splunk UI to denote the app this search should be dispatched in.", 
            "validation": ""
          }, 
          "request.ui_dispatch_view": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies a field used by Splunk UI to denote the view this search should be displayed in.", 
            "validation": ""
          }, 
          "restart_on_searchpeer_add": {
            "datatype": "Boolean", 
            "default": "1", 
            "required": "false", 
            "summary": "Specifies whether to restart a real-time search managed by the scheduler when a search peer becomes available for this saved search.\n\nNOTE: The peer can be a newly added peer or a peer that has been down and has become available.", 
            "validation": ""
          }, 
          "run_on_startup": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "Indicates whether this search runs when Splunk starts. If it does not run on startup, it runs at the next scheduled time.\n\nSplunk recommends that you set run_on_startup to true for scheduled searches that populate lookup tables.", 
            "validation": "validate(is_bool($run_on_startup$), \"Value of argument 'run_on_startup' must be a boolean\")"
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The search to save.", 
            "validation": ""
          }, 
          "vsid": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Defines the viewstate id associated with the UI view listed in 'displayview'.\n\nMust match up to a stanza in viewstates.conf.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create saved search."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Creates a saved search.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to the configuration of saved searches."
  }, 
  "saved/searches/{name}": {
    "methods": {
      "DELETE": {
        "config": "savedsearches", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete saved search."
          }, 
          "404": {
            "summary": "Saved search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Deletes this saved search.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "savedsearches", 
        "params": {
          "earliest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "If the search is scheduled display scheduled times starting from this time", 
            "validation": ""
          }, 
          "latest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "If the search is scheduled display scheduled times ending at this time", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view saved search."
          }, 
          "404": {
            "summary": "Saved search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information on this saved search.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "savedsearches", 
        "params": {
          "action.*": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.auth_password": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.auth_username": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.bcc": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.cc": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.command": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.format": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.from": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.hostname": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.inline": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.mailserver": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.maxresults": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.maxtime": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.pdfview": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.preprocess_results": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.reportPaperOrientation": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.reportPaperSize": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.reportServerEnabled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.reportServerURL": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.sendpdf": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.sendresults": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.subject": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.to": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.track_alert": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.ttl": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.use_ssl": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.use_tls": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.email.width_sort_columns": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.populate_lookup": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.populate_lookup.command": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.populate_lookup.dest": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.populate_lookup.hostname": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.populate_lookup.maxresults": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.populate_lookup.maxtime": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.populate_lookup.track_alert": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.populate_lookup.ttl": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.rss": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.rss.command": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.rss.hostname": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.rss.maxresults": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.rss.maxtime": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.rss.track_alert": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.rss.ttl": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.script": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.script.command": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.script.filename": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.script.hostname": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.script.maxresults": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.script.maxtime": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.script.track_alert": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.script.ttl": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index._name": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index.command": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index.hostname": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index.inline": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index.maxresults": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index.maxtime": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index.track_alert": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "action.summary_index.ttl": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "actions": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert.digest_mode": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert.expires": {
            "datatype": "INHERITED", 
            "default": "24h", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert.severity": {
            "datatype": "INHERITED", 
            "default": "3", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert.suppress": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert.suppress.fields": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert.suppress.period": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert.track": {
            "datatype": "INHERITED", 
            "default": "auto", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert_comparator": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert_condition": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert_threshold": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "alert_type": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "args.*": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "cron_schedule": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "description": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dispatch.*": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dispatch.buckets": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint($dispatch.buckets$) AND $dispatch.buckets$>=0, \"Value of argument 'dispatch.buckets' must be a non-negative integer\")"
          }, 
          "dispatch.earliest_time": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dispatch.latest_time": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dispatch.lookups": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($dispatch.lookups$), \"Value of argument 'dispatch.lookups' must be a boolean\")"
          }, 
          "dispatch.max_count": {
            "datatype": "INHERITED", 
            "default": "500000", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint($dispatch.max_count$) AND $dispatch.max_count$>=0, \"Value of argument 'dispatch.max_count' must be a non-negative integer\")"
          }, 
          "dispatch.max_time": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dispatch.reduce_freq": {
            "datatype": "INHERITED", 
            "default": "10", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dispatch.rt_backfill": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "dispatch.spawn_process": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($dispatch.spawn_process$), \"Value of argument 'dispatch.spawn_process' must be a boolean\")"
          }, 
          "dispatch.time_format": {
            "datatype": "INHERITED", 
            "default": "%FT%T.%Q%:z", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_time_format($dispatch.time_format$), \"Value of argument 'dispatch.time_format' must be a time format string\")"
          }, 
          "dispatch.ttl": {
            "datatype": "INHERITED", 
            "default": "2p", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "displayview": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "is_scheduled": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($is_scheduled$), \"Value of argument 'is_scheduled' must be a boolean\")"
          }, 
          "is_visible": {
            "datatype": "INHERITED", 
            "default": "true", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($is_visible$), \"Value of argument 'is_visible' must be a boolean\")"
          }, 
          "max_concurrent": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(isint($max_concurrent$) AND $max_concurrent$>=0, \"Value of argument 'max_concurrent' must be a non-negative integer\")"
          }, 
          "next_scheduled_time": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "qualifiedSearch": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "realtime_schedule": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($realtime_schedule$), \"Value of argument 'realtime_schedule' must be a boolean\")"
          }, 
          "request.ui_dispatch_app": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "request.ui_dispatch_view": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "restart_on_searchpeer_add": {
            "datatype": "INHERITED", 
            "default": "1", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "run_on_startup": {
            "datatype": "INHERITED", 
            "default": "0", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": "validate(is_bool($run_on_startup$), \"Value of argument 'run_on_startup' must be a boolean\")"
          }, 
          "search": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "vsid": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "false", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit saved search."
          }, 
          "404": {
            "summary": "Saved search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates this saved search.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "saved/searches/{name}/acknowledge": {
    "methods": {
      "POST": {
        "config": "savedsearches", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Suppression was acknowledged successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to acknowledge the suppression."
          }, 
          "404": {
            "summary": "Named save search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Acknowledge the suppression of the alerts from this saved search and resume alerting. Action available only with POST", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "saved/searches/{name}/dispatch": {
    "methods": {
      "POST": {
        "config": "savedsearches", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Dispatched the saved search successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to dispatch the saved search."
          }, 
          "404": {
            "summary": "Named save search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Dispatch the saved search just like the scheduler would. Action available only through POST. The following optional arguments are accepted:\ndispatch.now:    [time] dispatch the search as if it this was the current time \ndispatch.*:      any dispatch.* field of the search can be overriden\nnow:             [time] deprecated, same as dispatch.now use that instead\ntrigger_actions: [bool] whether to trigger alert actions \nforce_dispatch:  [bool] should a new search be started even if another instance of this search is already running", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "saved/searches/{name}/history": {
    "methods": {
      "GET": {
        "config": "savedsearches", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Retrieved the dispatch history successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to retrieve dispatch history for this saved search."
          }, 
          "404": {
            "summary": "Named save search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Get a list of available search jobs created from this saved search", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "saved/searches/{name}/scheduled_times": {
    "methods": {
      "GET": {
        "config": "savedsearches", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Scheduled times returned successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to get scheduled times."
          }, 
          "404": {
            "summary": "Scheduled times do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the scheduled times for a saved search. Specify a time range for the data returned using earliest_time and latest_time parameters.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "saved/searches/{name}/suppress": {
    "methods": {
      "GET": {
        "config": "savedsearches", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Retrieved/updated the suppression state successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to retrieve/update the suppression state."
          }, 
          "404": {
            "summary": "Named save search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Check the suppression state of alerts from this saved search.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "scheduled/views": {
    "methods": {
      "GET": {
        "config": "savedsearches", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view scheduled view."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists all scheduled view objects", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for management of scheduled (for pdf delivery) views. Scheduled views are dummy/noop scheduled saved searches that email a pdf version of a view"
  }, 
  "scheduled/views/{name}": {
    "methods": {
      "DELETE": {
        "config": "savedsearches", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete scheduled view."
          }, 
          "404": {
            "summary": "Scheduled view does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete a scheduled view", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "savedsearches", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view scheduled view."
          }, 
          "404": {
            "summary": "Scheduled view does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List one scheduled view object", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "savedsearches", 
        "params": {
          "action.email*": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Wildcard argument that accepts any email action.", 
            "validation": ""
          }, 
          "action.email.to": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Comma or semicolon separated list of email addresses to send the view to", 
            "validation": ""
          }, 
          "cron_schedule": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The cron schedule to use for delivering the view", 
            "validation": ""
          }, 
          "description": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "User readable description of this scheduled view object", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "0", 
            "required": "false", 
            "summary": "Whether this object is enabled or disabled", 
            "validation": ""
          }, 
          "is_scheduled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "true", 
            "summary": "Whether this pdf delivery should be scheduled", 
            "validation": "validate(is_bool($is_scheduled$), \"Value of argument 'is_scheduled' must be a boolean\")"
          }, 
          "next_scheduled_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The next time when the view will be delivered. Ignored on edit, here only for backwards compatability", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit scheduled view."
          }, 
          "404": {
            "summary": "Scheudled view does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Edit a scheduled view, e.g. change schedule, enable disable schedule etc", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "scheduled/views/{name}/dispatch": {
    "methods": {
      "POST": {
        "config": "savedsearches", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Dispatched the scheduled view successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to dispatch a scheduled view."
          }, 
          "404": {
            "summary": "Named view does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Dispatch the scheduled search (powering the scheduled view) just like the scheduler would. Action available only through POST. The following optional arguments are accepted:\"dispatch.now:    [time] dispatch the search as if it this was the current time\ndispatch.*:      any dispatch.* field of the search can be overriden\nnow:             [time] deprecated, same as dispatch.now use that instead\ntrigger_actions: [bool] whether to trigger the alert actions\nforce_dispatch:  [bool] should a new search be started even if another instance of this search is already running", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "scheduled/views/{name}/history": {
    "methods": {
      "GET": {
        "config": "savedsearches", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Retrieved scheduled view history successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to retrieve scheduled view history."
          }, 
          "404": {
            "summary": "Named view does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Get a list of search jobs used to deliver this scheduled view", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "scheduled/views/{name}/scheduled_times": {
    "methods": {
      "GET": {
        "config": "savedsearches", 
        "params": {
          "&lt;arbitrary_key&gt;": {
            "datatype": "UNDONE", 
            "default": "", 
            "required": "false", 
            "summary": "UNDONE", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Scheduled times returned successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to access scheduled times."
          }, 
          "404": {
            "summary": "Scheudled times do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the scheduled times for a scheduled view. Specify a time range for the data returned using earliest_time and latest_time parameters.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "search/distributed/config": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view configuration for distributed search."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists the configuration options for the distributed search system.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to Splunk's distributed search options.  This option is not for adding search peers."
  }, 
  "search/distributed/config/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete configuration for distributed search."
          }, 
          "404": {
            "summary": "Configuration for distributed search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Disables the distributed search feature.  Note that \"distributedSearch\" is the only valid name here.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view configuration for distributed search."
          }, 
          "404": {
            "summary": "Configuration for distributed search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Displays configuration options.  Note that \"distributedSearch\" is the only valid name here.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "autoAddServers": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, automatically add all discovered servers.", 
            "validation": ""
          }, 
          "blacklistNames": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A comma-separated list of servers that you do not want to peer with. \n\nServers are the 'server name' that is created at startup time.", 
            "validation": ""
          }, 
          "blacklistURLs": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a comma separated list of server names or URIs to specify servers to blacklist.\n\nYou can blacklist on server name or server URI (x.x.x.x:port).", 
            "validation": ""
          }, 
          "checkTimedOutServersFrequency": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Rechecks servers at the specified frequency (in seconds).  If this is set to 0, then no recheck occurs. Defaults to 60.\n\nThis attribute is ONLY relevant if removeTimedOutServers is set to true. If removeTimedOutServers is false, this attribute is ignored.\n", 
            "validation": ""
          }, 
          "connectionTimeout": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Amount of time, in seconds, to use as a timeout during search peer connection establishment.", 
            "validation": ""
          }, 
          "disabled": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, disables the distributed search.\n\nDefaults to false (the distributed search is enabled).", 
            "validation": ""
          }, 
          "heartbeatFrequency": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "The period between heartbeat messages, in seconds. \n\nUse 0 to disable sending of heartbeats. Defaults to 0.", 
            "validation": ""
          }, 
          "heartbeatMcastAddr": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify an IP address to set a multicast address where each Splunk server sends and listens for heart beat messages.\n\nThis allows Splunk servers to auto-discover other Splunk servers on your network. Defaults to 224.0.0.37.", 
            "validation": ""
          }, 
          "heartbeatPort": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a port to set the heartbeat port where each Splunk server sends and listens for heart beat messages.\n\nThis allows Splunk servers to auto-discover other Splunk servers on the network. Defaults to 8888.", 
            "validation": ""
          }, 
          "receiveTimeout": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Amount of time in seconds to use as a timeout while trying to read/receive data from a search peer.", 
            "validation": ""
          }, 
          "removedTimedOutServers": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, removes a server connection that cannot be made within serverTimeout.\n\nIf false, every call to that server attempts to connect. This may result in a slow user interface.\n\nDefaults to false.", 
            "validation": ""
          }, 
          "sendTimeout": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Amount of time in seconds to use as a timeout while trying to write/send data to a search peer.", 
            "validation": ""
          }, 
          "serverTimeout": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Deprected. Use connectionTimeout, sendTimeout, and receiveTimeout.", 
            "validation": ""
          }, 
          "servers": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a comma-separated list of server to set the initial list of servers.  \n\nIf operating completely in autoAddServers mode (discovering all servers), there is no need to list any servers here.", 
            "validation": ""
          }, 
          "shareBundles": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Indicates whether this server uses bundle replication to share search time configuration with search peers. \n\nIf set to false, the search head assumes that the search peers can access the correct bundles using an NFS share and have correctly configured the options listed under: \"SEARCH HEAD BUNDLE MOUNTING OPTIONS.\"\n\nDefaults to true.", 
            "validation": ""
          }, 
          "skipOurselves": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If set to true, this server does NOT participate as a server in any search or other call.\n\nThis is used for building a node that does nothing but merge the results from other servers. \n\nDefaults to false.", 
            "validation": ""
          }, 
          "statusTimeout": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Set connection timeout when gathering a search peer's basic info (/services/server/info). Defaults to 10.\n\nNote: Read/write timeouts are automatically set to twice this value.\n", 
            "validation": ""
          }, 
          "ttl": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Time to live (ttl) of the heartbeat messages. Defaults to 1 (this subnet).\n\nIncreasing this number allows the UDP multicast packets to spread beyond the current subnet to the specified number of hops.\n\nNOTE:  This only works if routers along the way are configured to pass UDP multicast packets.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit configuration for distributed search."
          }, 
          "404": {
            "summary": "Configuration for distributed search does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Update the configuration for the distributed search feature.  Note that \"distributedSearch\" is the only valid name here.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "search/distributed/peers": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "discoveredPeersOnly": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "If set to true, only list peers that have been auto-discovered.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view search peer."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns a list of configured search peers that this search head is configured to distribute searches to. This includes configured search peers that have been disabled.", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "", 
        "params": {
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The name of the search peer.\n\nDefined as hostname:port, where port is the management port.", 
            "validation": ""
          }, 
          "remotePassword": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The password of the remote user.\n\nThis is used to authenicate with the search peer to exchange certificates.", 
            "validation": ""
          }, 
          "remoteUsername": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The username of a user with admin privileges in the search peer server.\n\nThis is used to exchange certificates.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create search peer."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Adds a new search peer.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides distributed peer server management.\n\nA search peer is defined as a splunk server to which another splunk server distributes searches. The splunk server where the search request originates is referred to as the search head."
  }, 
  "search/distributed/peers/{name}": {
    "methods": {
      "DELETE": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete search peer."
          }, 
          "404": {
            "summary": "Search peer does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Removes the distributed search peer specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "", 
        "params": {
          "discoveredPeersOnly": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "If true, return only auto-discovered search peers.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view search peer."
          }, 
          "404": {
            "summary": "Search peer does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns information about the distributed search peer specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "remotePassword": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }, 
          "remoteUsername": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit search peer."
          }, 
          "404": {
            "summary": "Search peer does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Update the configuration of the distributed search peer specified by {name}.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "search/fields": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }
        }, 
        "summary": "Returns a list of fields registered for field configuration.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides management for search field configurations.\n\nField configuration is specified in $SPLUNK_HOME/etc/system/default/fields.conf, with overriden values in  $SPLUNK_HOME/etc/system/local/fields.conf."
  }, 
  "search/fields/{field_name}": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }
        }, 
        "summary": "Retrieves information about the named field.", 
        "urlParams": {
          "field_name": {
            "required": "true", 
            "summary": "field_name"
          }
        }
      }
    }
  }, 
  "search/fields/{field_name}/tags": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "Because fields exist only at search time, this endpoint returns a 200 response for any non-empty request.", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "404": {
            "summary": "Named field does not exist."
          }
        }, 
        "summary": "Returns a list of tags that have been associated with the field specified by {field_name}.", 
        "urlParams": {
          "field_name": {
            "required": "true", 
            "summary": "field_name"
          }
        }
      }, 
      "POST": {
        "params": {
          "add": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The tag to attach to this <code>field_name:value</code> combination.", 
            "validation": ""
          }, 
          "delete": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The tag to remove to this <code>field_name::value</code> combination.", 
            "validation": ""
          }, 
          "value": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The specific field value on which to bind the tags.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Tags updated."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }
        }, 
        "summary": "Update the tags associated with the field specified by {field_name}.\n\nThe <code>value</code> parameter specifies the specific value on which to bind tag actions. Multiple tags can be attached by passing multiple add or delete form parameters. The server processes all of the adds first, and then processes the deletes.\n\nYou must specify at least one <code>add</code> or <code>delete</code> parameter.", 
        "urlParams": {
          "field_name": {
            "required": "true", 
            "summary": "field_name"
          }
        }
      }
    }
  }, 
  "search/jobs": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }
        }, 
        "summary": "Returns a list of current searches. \n\nOptional filter arguments can be passed to specify searches. The user id is implied by the authentication to the call. See the response properties for <code>/search/jobs/{search_id}</code> for descriptions of the job properties.", 
        "urlParams": {}
      }, 
      "POST": {
        "params": {
          "auto_cancel": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "If specified, the job automatically cancels after this many seconds of inactivity.  (0 means never auto-cancel)", 
            "validation": ""
          }, 
          "auto_finalize_ec": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Auto-finalize the search after at least this many events have been processed. \n\nSpecify <code>0</code> to indicate no limit.", 
            "validation": ""
          }, 
          "auto_pause": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "If specified, the job automatically cancels after this many seconds of inactivity.  (0 means never auto-pause)", 
            "validation": ""
          }, 
          "earliest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a time string. Sets the earliest (inclusive), respectively, time bounds for the search. \n\nThe time string can be either a UTC time (with fractional seconds), a relative time specifier (to now) or a formatted time string. (Also see comment for the search_mode variable.)", 
            "validation": ""
          }, 
          "enable_lookups": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "Indicates whether lookups should be applied to events. \n\nSpecifying true (the default) may slow searches significantly depending on the nature of the lookups.\n", 
            "validation": ""
          }, 
          "exec_mode": {
            "datatype": "Enum", 
            "default": "normal", 
            "required": "false", 
            "summary": "Valid values: (blocking &#124; oneshot &#124; normal)\n\nIf set to normal, runs an asynchronous search. \n\nIf set to blocking, returns the sid when the job is complete. \n\nIf set to oneshot, returns results in the same call.", 
            "validation": ""
          }, 
          "force_bundle_replication": {
            "datatype": "Boolean", 
            "default": "false", 
            "required": "false", 
            "summary": "Specifies whether this search should cause (and wait depending on the value of sync_bundle_replication) for bundle synchronization with all search peers.", 
            "validation": ""
          }, 
          "id": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Optional string to specify the search ID (<code>&lt:sid&gt;</code>).  If unspecified, a random ID is generated.", 
            "validation": ""
          }, 
          "latest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a time string. Sets the latest (exclusive), respectively, time bounds for the search. \n\nThe time string can be either a UTC time (with fractional seconds), a relative time specifier (to now) or a formatted time string. (Also see comment for the search_mode variable.)", 
            "validation": ""
          }, 
          "max_count": {
            "datatype": "Number", 
            "default": "10000", 
            "required": "false", 
            "summary": "The number of events that can be accessible in any given status bucket. \n\nAlso, in transforming mode, the maximum number of results to store. Specifically, in all calls, <code>codeoffset+count <= max_count</code>.", 
            "validation": ""
          }, 
          "max_time": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "The number of seconds to run this search before finalizing. Specify <code>0</code> to never finalize.", 
            "validation": ""
          }, 
          "namespace": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The application namespace in which to restrict searches. \n\nThe namespace corresponds to the identifier recognized in the <code>/services/apps/local</code> endpoint. ", 
            "validation": ""
          }, 
          "now": {
            "datatype": "String", 
            "default": "current system time", 
            "required": "false", 
            "summary": "Specify a time string to set the absolute time used for any relative time specifier in the search. Defaults to the current system time.\n\nYou can specify a relative time modifier for this parameter. For example, specify <code>+2d</code> to specify the current time plus two days.\n\nIf you specify a relative time modifier both in this parameter and in the search string, the search string modifier takes precedence.\n\nRefer to [[Documentation:Splunk:SearchReference:SearchTimeModifiers|Time modifiers for search]] for details on specifying relative time modifiers.", 
            "validation": ""
          }, 
          "reduce_freq": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Determines how frequently to run the MapReduce reduce phase on accumulated map values.", 
            "validation": ""
          }, 
          "reload_macros": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "Specifies whether to reload macro definitions from <code>macros.conf</code>. \n\nDefault is true.", 
            "validation": ""
          }, 
          "remote_server_list": {
            "datatype": "String", 
            "default": "empty list", 
            "required": "false", 
            "summary": "Comma-separated list of (possibly wildcarded) servers from which raw events should be pulled. This same server list is to be used in subsearches.", 
            "validation": ""
          }, 
          "required_field_list": {
            "datatype": "String", 
            "default": "empty list", 
            "required": "false", 
            "summary": "Deprecated. Use rf instead. \n\nA comma-separated list of required fields that, even if not referenced or used directly by the search,is still included by the events and summary endpoints.", 
            "validation": ""
          }, 
          "rf": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Adds a required field to the search. There can be multiple <code>rf</code> POST arguments to the search.\n\nConsider using this form of passing the required fields to the search instead of the deprecated <code>required_field_list</code>. If both <code>rf</code> and <code>required_field_list</code> are supplied, the union of the two lists is used.", 
            "validation": ""
          }, 
          "rt_blocking": {
            "datatype": "Boolean", 
            "default": "false", 
            "required": "false", 
            "summary": " For a realtime search, indicates if the indexer blocks if the queue for this search is full.", 
            "validation": ""
          }, 
          "rt_indexfilter": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "For a realtime search, indicates if the indexer prefilters events.", 
            "validation": ""
          }, 
          "rt_maxblocksecs": {
            "datatype": "Number", 
            "default": "60", 
            "required": "false", 
            "summary": "For a realtime search with rt_blocking set to true, the maximum time to block.\n\nSpecify <code>0</code> to indicate no limit.", 
            "validation": ""
          }, 
          "rt_queue_size": {
            "datatype": "Number", 
            "default": "10000 events", 
            "required": "false", 
            "summary": "For a realtime search, the queue size (in events) that the indexer should use for this search.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "Search", 
            "default": "", 
            "required": "true", 
            "summary": "The search language string to execute, taking results from the local and remote servers.\n\nExamples:\n\n  \"search *\"\n\n  \"search * | outputcsv\"", 
            "validation": ""
          }, 
          "search_listener": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Registers a search state listener with the search.\n\nUse the format <code>search_state;results_condition;http_method;uri;</code>\n\nFor example: <code>search_listener=onResults;true;POST;/servicesNS/admin/search/saved/search/foobar/notify;</code>\n", 
            "validation": ""
          }, 
          "search_mode": {
            "datatype": "Enum", 
            "default": "normal", 
            "required": "false", 
            "summary": "Valid values: (normal &#124; realtime)\n\nIf set to realtime, search runs over live data. A realtime search may also be indicated by earliest_time and latest_time variables starting with 'rt' even if the search_mode is set to normal or is unset. For a real-time search, if both earliest_time and latest_time are both exactly 'rt', the search represents all appropriate live data received since the start of the search. \n\nAdditionally, if earliest_time and/or latest_time are 'rt' followed by a relative time specifiers then a sliding window is used where the time bounds of the window are determined by the relative time specifiers and are continuously updated based on the wall-clock time.", 
            "validation": ""
          }, 
          "spawn_process": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "Specifies whether the search should run in a separate spawned process. Default is true.", 
            "validation": ""
          }, 
          "status_buckets": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "The most status buckets to generate.\n\n<code>0</code> indicates to not generate timeline information.", 
            "validation": ""
          }, 
          "sync_bundle_replication": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies whether this search should wait for bundle replication to complete.", 
            "validation": ""
          }, 
          "time_format": {
            "datatype": "String", 
            "default": "ISO-8601", 
            "required": "false", 
            "summary": "Used to convert a formatted time string from {start,end}_time into UTC seconds. It defaults to ISO-8601.", 
            "validation": ""
          }, 
          "timeout": {
            "datatype": "Number", 
            "default": "86400", 
            "required": "false", 
            "summary": "The number of seconds to keep this search after processing has stopped.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }
        }, 
        "summary": "Starts a new search, returning the search ID (<code>&lt;sid&gt;</code>).\n\nThe search parameter is a search language string that specifies the search. Often you create a search specifying just the search parameter. Use the other parameters to customize a search to specific needs.\n\nUse the returned  (<code>&lt;sid&gt;</code>) in the following endpoints to view and manage the search:\n\n:search/jobs/{search_id}: View the status of this search job.\n\n:search/jobs/{search_id}/control: Execute job control commands, such as pause, cancel, preview, and others.\n\n:search/jobs/{search_id}/events: View a set of untransformed events for the search.\n\n:search/jobs/{search_id}/results: View results of the search.\n\n:search/jobs/{search_id}/results_preview: Preview results of a search that has not completed\n\n:search/jobs/{search_id}/search.log: View the log file generated by the search.\n\n:search/jobs/{search_id}/summary: View field summary information\n\n:search/jobs/{search_id}/timeline: View event distribution over time.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides listings for search jobs."
  }, 
  "search/jobs/export": {
    "methods": {
      "GET": {
        "params": {
          "auto_cancel": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "auto_finalize_ec": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "auto_pause": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "earliest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "enable_lookups": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "force_bundle_replication": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "id": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "latest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "max_time": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "namespace": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "now": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "reduce_freq": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "reload_macros": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "remote_server_list": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "required_field_list": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "rf": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "rt_blocking": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "rt_indexfilter": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "rt_maxblocksecs": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "rt_queue_size": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "search_listener": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "search_mode": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "sync_bundle_replication": {
            "datatype": "Bool", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "time_format": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }, 
          "timeout": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Same as for POST search/jobs.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Searched successfully."
          }
        }, 
        "summary": "Performs a search identical to POST search/jobs, except the search does not create a search ID (<sid>) and the search streams results as they become available. Streaming of results is based on the search string.\n \nFor non-streaming searches, previews of the final results are available if preview is enabled. If preview is not enabled, it is better to use search/jobs with exec_mode=oneshot.", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for streaming of search results as the become available."
  }, 
  "search/jobs/{search_id}": {
    "methods": {
      "DELETE": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "404": {
            "summary": "Search job does not exist."
          }
        }, 
        "summary": "Deletes the search job specified by {search_id}.\n\n{search_id} is the <code>&lt;sid&gt;</code> field returned from the GET operation for the <code>search/jobs</code> endpoint.", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }, 
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "404": {
            "summary": "Search job does not exist."
          }
        }, 
        "summary": "Return summary information about the search job specified by {search_id}.\n\nYou can get a search ID from the <code><sid></code> field returned from the GET operation for the <code>search/jobs</code> endpoint.", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }
    }
  }, 
  "search/jobs/{search_id}/control": {
    "methods": {
      "POST": {
        "params": {
          "action": {
            "datatype": "Enum", 
            "default": "", 
            "required": "true", 
            "summary": "Valid values: (pause &#124; unpause &#124; finalize &#124; cancel &#124; touch &#124; setttl &#124; setpriority &#124; enablepreview &#124; disablepreview)\n\nThe control action to execute.\n\npause:  Suspends the execution of the current search.\n\nunpause:  Resumes the execution of the current search, if paused.\n\nfinalize:  Stops the search, and provides intermediate results to the /results endpoint.\n\ncancel:  Stops the current search and deletes the result cache.\n\ntouch:   Extends the expiration time of the search to now + ttl\n\nsetttl:  Change the ttl of the search. Arguments: ttl=&lt;number&gt;\n\nsetpriority:  Sets the priority of the search process. Arguments: priority=&lt;0-10&gt;\n\nenablepreview:  Enable preview generation (may slow search considerably).\n\ndisablepreview:  Disable preview generation.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit control action for search job."
          }, 
          "404": {
            "summary": "Search job does not exist."
          }
        }, 
        "summary": "Executes a job control command for the search specified by {search_id}.", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }
    }
  }, 
  "search/jobs/{search_id}/events": {
    "methods": {
      "GET": {
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "100", 
            "required": "false", 
            "summary": "The maximum number of results to return. If value is set to <code>0</code>, then all available results are returned. Default value is <code>100</code>.", 
            "validation": ""
          }, 
          "earliest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A time string representing the earliest (inclusive), respectively, time bounds for the results to be returned. If not specified, the range applies to all results found.", 
            "validation": ""
          }, 
          "f": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A field to return for the event set. \n\nYou can pass multiple <code>POST f</code> arguments if multiple field are required. If <code>field_list</code> and <code>f</code> are provided, the union of the lists is used.", 
            "validation": ""
          }, 
          "field_list": {
            "datatype": "String", 
            "default": "<code>*</code>", 
            "required": "false", 
            "summary": "Deprecated. Consider using <code>f</code>.\n\nA comma-separated list of the fields to return for the event set.", 
            "validation": ""
          }, 
          "latest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A time string representing the latest (exclusive), respectively, time bounds for the results to be returned. If not specified, the range applies to all results found.", 
            "validation": ""
          }, 
          "max_lines": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "The maximum lines that any single event's _raw field should contain. \n\nSpecify <code>0</code> to specify no limit.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "The first result (inclusive) from which to begin returning data. \n\nThis value is 0-indexed. Default value is 0. \n\nIn 4.1+, negative offsets are allowed and are added to <code>count</code> to compute the absolute offset (for example, <code>offset=-1</code> is the last available offset. Offsets in the results are always absolute and never negative.", 
            "validation": ""
          }, 
          "output_mode": {
            "datatype": "Enum", 
            "default": "xml", 
            "required": "false", 
            "summary": "Valid values: (csv &#124; raw &#124; xml &#124; json)\n\nSpecifies what format the output should be returned in.", 
            "validation": ""
          }, 
          "output_time_format": {
            "datatype": "String", 
            "default": "<code>time_format</code>", 
            "required": "false", 
            "summary": "Formats a UTC time. Defaults to what is specified in <code>time_format</code>.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The post processing search to apply to results. Can be any valid search language string.", 
            "validation": ""
          }, 
          "segmentation": {
            "datatype": "String", 
            "default": "raw", 
            "required": "false", 
            "summary": "The type of segmentation to perform on the data. This incudes an option to perform k/v segmentation.\n", 
            "validation": ""
          }, 
          "time_format": {
            "datatype": "String", 
            "default": " %m/%d/%Y:%H:%M:%S", 
            "required": "false", 
            "summary": "Expression to convert a formatted time string from {start,end}_time into UTC seconds. \n\nIt defaults to %m/%d/%Y:%H:%M:%S", 
            "validation": ""
          }, 
          "truncation_mode": {
            "datatype": "String", 
            "default": "abstract", 
            "required": "false", 
            "summary": "Specifies how \"max_lines\" should be achieved.\n\nValid values are {<code>abstract</code>, <code>truncate</code>}. Default value is <code>abstract</code>.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "204": {
            "summary": "Search was found, but events are not yet ready.  Retry request."
          }, 
          "404": {
            "summary": "Search job does not exist."
          }
        }, 
        "summary": "Returns the events of the search specified by {search_id}. These events are the data from the search pipeline before the first \"transforming\" search command. This is the primary method for a client to fetch a set of UNTRANSFORMED events for the search job.\n\nThis endpoint is only valid if the status_buckets > 0 or the search has no transforming commands.\n\n", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }
    }
  }, 
  "search/jobs/{search_id}/results": {
    "methods": {
      "GET": {
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "100", 
            "required": "false", 
            "summary": "The maximum number of results to return. If value is set to <code>0</code>, then all available results are returned.", 
            "validation": ""
          }, 
          "f": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A field to return for the event set. \n\nYou can pass multiple <code>POST f</code> arguments if multiple field are required. If <code>field_list</code> and <code>f</code> are provided the union of the lists is used.", 
            "validation": ""
          }, 
          "field_list": {
            "datatype": "String", 
            "default": "<code>*</code>", 
            "required": "false", 
            "summary": "Specify a comma-separated list of the fields to return for the event set.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "The first result (inclusive) from which to begin returning data. \n\nThis value is 0-indexed. Default value is 0. \n\nIn 4.1+, negative offsets are allowed and are added to <code>count</code> to compute the absolute offset (for example, <code>offset=-1</code> is the last available offset). \n\nOffsets in the results are always absolute and never negative.", 
            "validation": ""
          }, 
          "output_mode": {
            "datatype": "Enum", 
            "default": "", 
            "required": "false", 
            "summary": "Valid values: (csv &#124; raw &#124; xml &#124; json)\n\nSpecifies what format the output should be returned in.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The post processing search to apply to results. Can be any valid search language string.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "204": {
            "summary": "Search was found, but events are not yet ready.  Retry request."
          }, 
          "404": {
            "summary": "Search job does not exist."
          }
        }, 
        "summary": "Returns the results of the search specified by {search_id}. This is the table that exists after all processing from the search pipeline has completed.\n\nThis is the primary method for a client to fetch a set of TRANSFORMED events. If the dispatched search does not include a transforming command, the effect is the same as get_events, however with fewer options.", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }
    }
  }, 
  "search/jobs/{search_id}/results_preview": {
    "methods": {
      "GET": {
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "100", 
            "required": "false", 
            "summary": "The maximum number of results to return. \n\nIf value is set to <code>0</code>, then all available results are returned.", 
            "validation": ""
          }, 
          "f": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A field to return for the event set. \n\nYou can pass multiple <code>POST f</code> arguments if multiple field are required. If <code>field_list</code> and <code>f</code> are provided the union of the lists is used.", 
            "validation": ""
          }, 
          "field_list": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a comma-separated list of the fields to return for the event set.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "The first result (inclusive) from which to begin returning data. \n\nThis value is 0-indexed. Default value is 0. \n\nIn 4.1+, negative offsets are allowed and are added to <code>count</code> to compute the absolute offset (for example, <code>offset=-1</code> is the last available offset). \n\nOffsets in the results are always absolute and never negative.", 
            "validation": ""
          }, 
          "output_mode": {
            "datatype": "String", 
            "default": "xml", 
            "required": "false", 
            "summary": "Specifies what format the output should be returned in.\n\nValid values are:\n\n  csv\n  raw\n  xml\n  json\n", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The post processing search to apply to results. Can be any valid search language string.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "204": {
            "summary": "Search was found, but events are not yet ready.  Retry request."
          }, 
          "404": {
            "summary": "Search job does not exist."
          }
        }, 
        "summary": "Returns the intermediate preview results of the search specified by {search_id}. When the job is complete, this gives the same response as /search/jobs/{search_id}/results.\n\nThis endpoint is only valid if preview is enabled. ", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }
    }
  }, 
  "search/jobs/{search_id}/search.log": {
    "methods": {
      "GET": {
        "params": {
          "attachment": {
            "datatype": "Boolean", 
            "default": "false", 
            "required": "false", 
            "summary": "If true, returns search.log as an attachment. Otherwise, streams search.log.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "204": {
            "summary": "Search was found, but events are not yet ready.  Retry request."
          }, 
          "404": {
            "summary": "Search log does not exist."
          }
        }, 
        "summary": "Returns the search.log for the search job specified by {search_id}.", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }
    }
  }, 
  "search/jobs/{search_id}/summary": {
    "methods": {
      "GET": {
        "params": {
          "earliest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Time string representing the earliest (inclusive), respectively, time bounds for the search. \n\nThe time string can be either a UTC time (with fractional seconds), a relative time specifier (to now) or a formatted time string. (Also see comment for the search_mode variable.)", 
            "validation": ""
          }, 
          "f": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A field to return for the event set.\n\nYou can pass multiple <code>POST f</code> arguments if multiple field are required. If <code>field_list</code> and <code>f</code> are provided, the union of the lists is used.", 
            "validation": ""
          }, 
          "field_list": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Deprecated. Consider using <code>f</code>.\n\nA comma-separated list of the fields to return for the event set.", 
            "validation": ""
          }, 
          "latest_time": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Time string representing the latest (exclusive), respectively, time bounds for the search. \n\nThe time string can be either a UTC time (with fractional seconds), a relative time specifier (to now) or a formatted time string. (Also see comment for the search_mode variable.) ", 
            "validation": ""
          }, 
          "min_freq": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "For each key, the fraction of results this key must occur in to be displayed.\n\nExpress the fraction as a number between 0 and 1.", 
            "validation": ""
          }, 
          "output_time_format": {
            "datatype": "String", 
            "default": "%FT%T.%Q%:z", 
            "required": "false", 
            "summary": "Formats a UTC time. Defaults to what is specified in <code>time_format</code>.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "Empty string", 
            "required": "false", 
            "summary": "Specifies a substring that all returned events should contain either in one of their values or tags.", 
            "validation": ""
          }, 
          "time_format": {
            "datatype": "String", 
            "default": " %m/%d/%Y:%H:%M:%", 
            "required": "false", 
            "summary": "Expression to convert a formatted time string from {start,end}_time into UTC seconds.\nIt defaults to %m/%d/%Y:%H:%M:%S", 
            "validation": ""
          }, 
          "top_count": {
            "datatype": "Number", 
            "default": "10", 
            "required": "false", 
            "summary": "For each key, specfies how many of the most frequent items to return.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "403": {
            "summary": "Insufficient permissions to view summary for search job."
          }, 
          "404": {
            "summary": "Summary for search job does not exist."
          }
        }, 
        "summary": "Returns \"getFieldsAndStats\" output of the so-far-read events.\n\nThis endpoint is only valid when status_buckets > 0. To guarantee a set of fields in the summary, when creating the search, use the <code>required_fields_list</code> or <code>rf</code> parameters.", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }
    }
  }, 
  "search/jobs/{search_id}/timeline": {
    "methods": {
      "GET": {
        "params": {
          "output_time_format": {
            "datatype": "String", 
            "default": "%FT%T.%Q%:z", 
            "required": "false", 
            "summary": "Formats a UTC time. Defaults to what is specified in <code>time_format</code>.", 
            "validation": ""
          }, 
          "time_format": {
            "datatype": "String", 
            "default": " %m/%d/%Y:%H:%M:%S", 
            "required": "false", 
            "summary": "Expression to convert a formatted time string from {start,end}_time into UTC seconds. \n\nIt defaults to %m/%d/%Y:%H:%M:%S", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "204": {
            "summary": "Search was found, but events are not yet ready.  Retry request."
          }, 
          "404": {
            "summary": "Timeline for search job does not exist."
          }
        }, 
        "summary": "Returns event distribution over time of the so-far-read untransformed events.\n\nThis endpoint is only valid when status_buckets > 0. To guarantee a set of fields in the summary, when creating the search, use the <code>required_fields_list</code> or <code>rf</code> parameters.", 
        "urlParams": {
          "search_id": {
            "required": "true", 
            "summary": "search_id"
          }
        }
      }
    }
  }, 
  "search/parser": {
    "methods": {
      "GET": {
        "params": {
          "enable_lookups": {
            "datatype": "Boolean", 
            "default": "false", 
            "required": "false", 
            "summary": "If <code>true</code>, reverse lookups are done to expand the search expression.", 
            "validation": ""
          }, 
          "output_mode": {
            "datatype": "String", 
            "default": "xml", 
            "required": "false", 
            "summary": "Specify output formatting. Select from either:\n\n  xml:  XML formatting\n  json: JSON formatting\n", 
            "validation": ""
          }, 
          "parse_only": {
            "datatype": "Boolean", 
            "default": "false", 
            "required": "false", 
            "summary": "If true, disables expansion of search due evaluation of subsearches, time term expansion, lookups, tags, eventtypes, sourcetype alias.", 
            "validation": ""
          }, 
          "q": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The search string to parse.", 
            "validation": ""
          }, 
          "reload_macros": {
            "datatype": "Boolean", 
            "default": "true", 
            "required": "false", 
            "summary": "If true, reload macro definitions from macros.conf.\n", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }
        }, 
        "summary": "Parses Splunk search language and returns semantic map.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provide search language parsing services."
  }, 
  "search/tags": {
    "methods": {
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }
        }, 
        "summary": "Returns a list of all search time tags.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides management of search time tags."
  }, 
  "search/tags/{tag_name}": {
    "methods": {
      "DELETE": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "404": {
            "summary": "Search tag does not exist."
          }
        }, 
        "summary": "Deletes the tag, and its associated field:value pair assignments. The resulting change in tags.conf is to set all field:value pairs to <code>disabled</code>.\n", 
        "urlParams": {
          "tag_name": {
            "required": "true", 
            "summary": "tag_name"
          }
        }
      }, 
      "GET": {
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "404": {
            "summary": "Search tag does not exist."
          }
        }, 
        "summary": "Returns a list of field:value pairs that have been associated with the tag specified by {tag_name}.", 
        "urlParams": {
          "tag_name": {
            "required": "true", 
            "summary": "tag_name"
          }
        }
      }, 
      "POST": {
        "params": {
          "add": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A field:value pair to tag with {tag_name}.", 
            "validation": ""
          }, 
          "delete": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "A field:value pair to remove from {tag_name}.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "201": {
            "summary": "Field successfuly added to tag."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }
        }, 
        "summary": "Updates the field:value pairs associated with {tag_name}. \n\nMultiple field:value pairs can be attached by passing multiple add or delete form parameters. The server processes all of the adds first, and then deletes.\n\nIf {tag_name} does not exist, then the tag is created inline. Notification is sent to the client using the HTTP 201 status.", 
        "urlParams": {
          "tag_name": {
            "required": "true", 
            "summary": "tag_name"
          }
        }
      }
    }
  }, 
  "search/timeparser": {
    "methods": {
      "GET": {
        "params": {
          "now": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The time to use as current time for relative time identifiers. \n\nCan itself either be a relative time (from the real \"now\" time) or an absolute time in the format specified by <code>time_format</code>.\n", 
            "validation": ""
          }, 
          "output_time_format": {
            "datatype": "String", 
            "default": "%FT%T.%Q%:z", 
            "required": "false", 
            "summary": "Used to format a UTC time. Defaults to the value of <code>time_format</code>.", 
            "validation": ""
          }, 
          "time": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The time argument to parse. \n\nAcceptable inputs are either a relative time identifier or an absolute time. Multiple time arguments can be passed by specifying multiple time parameters.\n", 
            "validation": ""
          }, 
          "time_format": {
            "datatype": "String", 
            "default": "%FT%T.%Q%:z", 
            "required": "false", 
            "summary": "The format (<code>strftime</code>) of the absolute time format passed in time. \n\nThis field is not used if a relative time identifier is provided. For absolute times, the default value is the ISO-8601 format.\n", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "204": {
            "summary": "No timeparser arguments given."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }
        }, 
        "summary": "Returns a lookup table of time arguments to absolute timestamps.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides time argument parsing."
  }, 
  "search/typeahead": {
    "methods": {
      "GET": {
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "", 
            "required": "true", 
            "summary": "The number of counts to return for this term.", 
            "validation": ""
          }, 
          "output_mode": {
            "datatype": "String", 
            "default": "xml", 
            "required": "false", 
            "summary": "Valid values: (xml &#124; json)\n\nFormat for the output.", 
            "validation": ""
          }, 
          "prefix": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The term for which to return typeahead results.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "204": {
            "summary": "No Content. The server successfully processed the request, but is not returning any content."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "403": {
            "summary": "Insufficient permissions to view typeahead results."
          }, 
          "405": {
            "summary": "Invalid method (only GET is supported)."
          }
        }, 
        "summary": "Returns a list of words or descriptions for possible auto-complete terms.\n\ncount is a required parameter to specify how many descriptions to list. prefix is a required parameter to specify a string for terms in your index.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides search string auto-complete suggestions."
  }, 
  "server/control": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view server controls."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Lists the actions that can be performed at this endpoint.", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows access to controls, such as restarting server."
  }, 
  "server/control/restart": {
    "methods": {
      "POST": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Restart requested successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to restart Splunk."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Restarts the Splunk server.", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for restarting Splunk."
  }, 
  "server/info": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view server configuration info."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Enumerates the following information about the running splunkd: \n\n  build\n  cpu_arch (CPU architecure)\n  guid (GUID for this splunk instance)\n  isFree\n  isTrial\n  licenseKeys (hashes)\n  licenseSignature\n  licenseState\n  license_labels\n  master_guid (GUID of the license master)\n  mode\n  os_build\n  os_name\n  os_version\n  rtsearch_enabled\n  serverName\n  version", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to configuration information about the server."
  }, 
  "server/info/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view server configuration info."
          }, 
          "404": {
            "summary": "Server configuration info does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Provides the identical information as /services/server/info. The only valid {name} here is server-info.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "server/logger": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view logger info."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Enumerates all splunkd logging categories, either specified in code or in $SPLUNK_HOME/etc/log.cfg.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to splunkd logging categories, either specified in code or in $SPLUNK_HOME/etc/log.cfg."
  }, 
  "server/logger/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view logger info."
          }, 
          "404": {
            "summary": "Logger info does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Describes a specific splunkd logging category.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "level": {
            "datatype": "Enum", 
            "default": "", 
            "required": "true", 
            "summary": "Valid values: (FATAL &#124; CRIT &#124; WARN &#124; INFO &#124; DEBUG)\n\nThe desired logging level for this category.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit logger configuration."
          }, 
          "404": {
            "summary": "Logger configuration does not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Sets the logging level for a specific logging category.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "server/settings": {
    "methods": {
      "GET": {
        "config": "", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view server settings."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the server configuration of an instance of Splunk.", 
        "urlParams": {}
      }
    }, 
    "summary": "Provides access to server configuration information for an instance of Splunk."
  }, 
  "server/settings/{name}": {
    "methods": {
      "GET": {
        "config": "", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view server settings."
          }, 
          "404": {
            "summary": "Server settings do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Returns the server configuration of this instance of Splunk.\n\n\"settings\" is the only valid value for {name} in this endpoint. This endpoint returns the same information as [[Documentation:Splunk:RESTAPI:RESTsystem#GET_server.2Fsettings|GET server/settings]].", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "", 
        "params": {
          "SPLUNK_DB": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Path to the default index for this instance of Splunk.\n\nThe default location is:\n\n$SPLUNK_HOME/var/lib/splunk/defaultdb/db/", 
            "validation": "is_dir(SPLUNK_DB)"
          }, 
          "enableSplunkWebSSL": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Toggles between https and http. If true, enables https and SSL for Splunk Web. ", 
            "validation": "is_bool(enableSplunkWebSSL)"
          }, 
          "host": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The default hostname to use for data inputs that do not override this setting.", 
            "validation": ""
          }, 
          "httpport": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies the port on which Splunk Web is listening for this instance of Splunk. Defaults to 8000. If using SSL, set to the HTTPS port number.\n\nhttpport must be present for SplunkWeb to start. If omitted or 0 the server will NOT start an http listener.", 
            "validation": ""
          }, 
          "mgmtHostPort": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify IP address:Port to set the managment port for splunkd. \n\nDefaults to 127.0.0.1:8089.", 
            "validation": ""
          }, 
          "minFreeSpace": {
            "datatype": "Number", 
            "default": "", 
            "required": "false", 
            "summary": "Specifies, in MB, a safe amount of space that must exist for splunkd to continue operating.\n\nminFreespace affects search and indexing:\n\nBefore attempting to launch a search, splunk requires this amount of free space on the filesystem where the dispatch directory is stored ($SPLUNK_HOME/var/run/splunk/dispatch).\n\nApplied similarly to the search quota values in authorize.conf and limits.conf.\n\nFor indexing, periodically, the indexer checks space on all partitions that contain splunk indexes as specified by indexes.conf.  When you need to clear more disk space, indexing is paused and Splunk posts a ui banner + warning.", 
            "validation": "validate(isint(minFreeSpace), \"Minimum free space must be an integer.\",minFreeSpace > 0, \"Minimum free space must be greater than zero.\")"
          }, 
          "pass4SymmKey": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Password string that is prepended to the splunk symmetric key to generate the final key that is used to sign all traffic between master/slave licenser.", 
            "validation": ""
          }, 
          "serverName": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify an ASCII String to set the name used to identify this Splunk instance for features such as distributed search. Defaults to <hostname>-<user running splunk>.", 
            "validation": ""
          }, 
          "sessionTimeout": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Specify a time range string to set the amount of time before a user session times out, expressed as a search-like time range. Default is 1h (one hour).\n\nFor example:\n\n24h: (24 hours)\n\n3d: (3 days)\n\n7200s: (7200 seconds, or two hours)\n", 
            "validation": ""
          }, 
          "startwebserver": {
            "datatype": "Boolean", 
            "default": "", 
            "required": "false", 
            "summary": "Specify 1 to enable Splunk Web. 0 disables Splunk Web. Default is 1.", 
            "validation": "is_bool(startwebserver)"
          }, 
          "trustedIP": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The IP address of the authenticating proxy. Set to a valid IP address to enable SSO.\n\nDisabled by default. Normal value is '127.0.0.1'", 
            "validation": "validate(match(trustedIP, \"^\\\\d{1,3}\\\\.\\\\d{1,3}\\\\.\\\\d{1,3}\\\\.\\\\d{1,3}$\"),\"Trusted IP must be an IP address (IPv4)\")"
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit server settings."
          }, 
          "404": {
            "summary": "Server settings do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Updates the server configuration of this instance of Splunk.\n\n\"settings\" is the only valid value for {name} in this endpoint.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }, 
  "storage/passwords": {
    "methods": {
      "GET": {
        "config": "app", 
        "params": {
          "count": {
            "datatype": "Number", 
            "default": "30", 
            "required": "false", 
            "summary": "Indicates the maximum number of entries to return. To return all entries, specify 0.", 
            "validation": ""
          }, 
          "offset": {
            "datatype": "Number", 
            "default": "0", 
            "required": "false", 
            "summary": "Index for first item to return.", 
            "validation": ""
          }, 
          "search": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "Search expression to filter the response. The response matches field values against the search expression. For example:\n\nsearch=foo matches any object that has \"foo\" as a substring in a field.\nsearch=field_name%3Dfield_value restricts the match to a single field. URI-encoding is required in this example.", 
            "validation": ""
          }, 
          "sort_dir": {
            "datatype": "Enum", 
            "default": "asc", 
            "required": "false", 
            "summary": "Valid values: (asc &#124; desc)\n\nIndicates whether to sort returned entries in ascending or descending order.", 
            "validation": ""
          }, 
          "sort_key": {
            "datatype": "String", 
            "default": "name", 
            "required": "false", 
            "summary": "Field to use for sorting.", 
            "validation": ""
          }, 
          "sort_mode": {
            "datatype": "Enum", 
            "default": "auto", 
            "required": "false", 
            "summary": "Valid values: (auto &#124; alpha &#124; alpha_case &#124; num)\n\nIndicates the collating sequence for sorting the returned entries.\nauto: If all values of the field are numbers, collate numerically. Otherwise, collate alphabetically.\nalpha: Collate alphabetically.\nalpha_case: Collate alphabetically, case-sensitive.\nnum: Collate numerically.", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view credentials."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List available credentials", 
        "urlParams": {}
      }, 
      "POST": {
        "config": "app", 
        "params": {
          "name": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "Username for the credentials", 
            "validation": ""
          }, 
          "password": {
            "datatype": "String", 
            "default": "", 
            "required": "true", 
            "summary": "The password for the credentials - this is the only part of the credentials that will be stored securely", 
            "validation": ""
          }, 
          "realm": {
            "datatype": "String", 
            "default": "", 
            "required": "false", 
            "summary": "The credential realm", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "201": {
            "summary": "Created successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to create credentials."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Create/edit new credentials", 
        "urlParams": {}
      }
    }, 
    "summary": "Allows for management of secure credentials. The password is encrypted with a secret key that resides on the same machine. The clear text passwords can be accessed by users that have access to this service. Only users with admin priviledges can access this endpoint.\n\n'''Note:''' This endpoint is new for Splunk 4.3. It replaces the deprecated endpoint accessible from <code>/admin/passwords/</code>."
  }, 
  "storage/passwords/{name}": {
    "methods": {
      "DELETE": {
        "config": "app", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Deleted successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to delete credentials."
          }, 
          "404": {
            "summary": "Credentials do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "Delete the identified credentials", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "GET": {
        "config": "app", 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Listed successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "403": {
            "summary": "Insufficient permissions to view credentials."
          }, 
          "404": {
            "summary": "Credentials do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }
        }, 
        "summary": "List only the credentials identified by the given id", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }, 
      "POST": {
        "config": "app", 
        "params": {
          "password": {
            "datatype": "INHERITED", 
            "default": "", 
            "required": "true", 
            "summary": "INHERITED", 
            "validation": ""
          }
        }, 
        "request": "", 
        "response": "", 
        "returns": {
          "200": {
            "summary": "Updated successfully."
          }, 
          "400": {
            "summary": "Request error.  See response body for details."
          }, 
          "401": {
            "summary": "Authentication failure: must pass valid credentials with request."
          }, 
          "402": {
            "summary": "The Splunk license in use has disabled this feature."
          }, 
          "403": {
            "summary": "Insufficient permissions to edit credentials."
          }, 
          "404": {
            "summary": "Credentials do not exist."
          }, 
          "409": {
            "summary": "Request error: this operation is invalid for this item.  See response body for details."
          }, 
          "500": {
            "summary": "Internal server error.  See response body for details."
          }, 
          "503": {
            "summary": "This feature has been disabled in Splunk configuration files."
          }
        }, 
        "summary": "Edit the identified credentials.", 
        "urlParams": {
          "name": {
            "required": "true", 
            "summary": "name"
          }
        }
      }
    }
  }
}
