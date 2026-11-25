import groovy.json.JsonOutput
import groovy.json.JsonSlurper

String base = System.getenv('BASE_URL') ?: 'http://127.0.0.1:8000'
JsonSlurper json = new JsonSlurper()
int failed = 0

Closure check = { String name, Closure body ->
    try {
        assert body()
        println "PASS ${name}"
    } catch (Throwable t) {
        failed++
        println "FAIL ${name}: ${t.message?.readLines()?.first()}"
    }
}

Closure http = { String method, String path, Map payload = null ->
    HttpURLConnection con = (HttpURLConnection) new URL(base + path).openConnection()
    con.requestMethod = method
    con.setRequestProperty('Content-Type', 'application/json')
    if (payload != null) {
        con.doOutput = true
        con.outputStream.withWriter { it << JsonOutput.toJson(payload) }
    }
    int code = con.responseCode
    InputStream stream = code < 400 ? con.inputStream : con.errorStream
    [code: code, body: stream ? json.parseText(stream.text) : null]
}

http('POST', '/api/reset')
List seed = json.parse(new File('app/seed.json'))
check('req01_groovy_products_complete') { http('GET', '/api/products').body.size() == seed.size() }
check('req02_groovy_login_ok') { http('POST', '/api/login', [username: 'alice', password: 'secret123']).code == 200 }
check('req02_groovy_login_rejects_bad_password') {
    http('POST', '/api/login', [username: 'alice', password: 'nope']).code == 401
}
System.exit(failed ? 1 : 0)
