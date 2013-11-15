var config = {
    authShimUrl: "https://www.authshim.com:5000/oauth2/",
    corsporxyUrl: "http://www.testapp.com:5002/corsproxy",
    boxUrl: "https://api.box.com/2.0"
}

var ofs = (function() {
    var client = function(url) {
        return boxClient;
    }
    return {
        client: client,
        foo: "whatever"
    };
})();

var getAccessToken = function() {
    // Borrowed from google
    // First, parse the query string
    var params = {}, queryString = location.hash.substring(1),
        regex = /([^&=]+)=([^&]*)/g, m;
    while (m = regex.exec(queryString)) {
      params[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
    }

    // returns undefined if it's missing
    return params['access_token'];
}

var boxClient = (function() {
    var auth = function(client_id, callback) {
        var redirectUrl = document.URL;
        // TODO: better more generalized string formatting
        var authUrl = config['authShimUrl'] + "box/auth?client_id=" + client_id + "&redirect_uri=" + redirectUrl;
        var receiveMessage = function(message) {
            token = message['data'];
            callback(null, boxFs(token), token);
        }
        window.addEventListener("message", receiveMessage, false);
        var newWindow = window.open(authUrl, "Auth to Box", "height=200,width=200");
    };

    return {
        auth: auth
    };
})()

var boxFs = function(accessToken) {
    var stat = function(path, callback) {
        if (path == "/") {
            makeBoxRequest("/folders/0", function(err, data) {
                if (err) {
                    callback(err);
                } else {
                    callback(null, postProcessStat(data));
                }
            });
        } else {
            // without a cache, need recursively build up
            // TODO
            callback(null, "can only do root path");
        }
    };

    var postProcessStat = function(boxFolderObject, basePath) {
        var type = "application/" + boxFolderObject["type"]
        var filename = boxFolderObject['name']
        var path = "";
        if (boxFolderObject['path_collection']) {
            boxFolderObject['path_collection']['entries'].forEach(function(item) {
                path += item['name'] + "/"

            });
        } else {
            path += basePath + '/';
        }
        path += filename;
        id = boxFolderObject['id'];
        
        return {
          path: path, // required
          filename: filename, // required
          type: type, // mimetype
          id: id
        }
    }

    var listContents = function(path, callback) {
        if (path == "/") {
            makeBoxRequest("/folders/0", function(err, data) {
                console.log(data);
                if (err) {
                    callback(err);
                } else {
                    var folder_stat = postProcessStat(data);
                    var contents = [];
                    folder_stat['contents'] = [];
                    data["item_collection"]["entries"].forEach(function(item) {
                        contents.push(postProcessStat(item, folder_stat['path']));
                    });
                    callback(null, contents);
                }
            });
        }
    };

    var idToPath = function(id, callback) {
        // TODO
    }

    var getTemporaryUrl = function(path, callback) {
        callback(null, accessToken);
    };


    var makeBoxRequest = function(urlEnd, callback) {
        // TODO: proper url join
        url = encodeURIComponent(config['boxUrl'] + urlEnd);

        $.ajax({
            type:"GET",
            beforeSend: function(request) {
                request.setRequestHeader("Authorization", "Bearer " + accessToken);
            },
            dataType: "json",
            url: config['corsporxyUrl'] + "?url=" + url,
            success: function(json) { callback(null, json) },
            error: function(error) { callback(error) }
        });
    }

    return {
        stat: stat,
        listContents: listContents,
        getTemporaryUrl: getTemporaryUrl 
    };
};
