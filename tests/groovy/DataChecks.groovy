import groovy.json.JsonSlurper

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

List products = new JsonSlurper().parse(new File('app/seed.json'))
List reqIds = new File('data/requirements.csv').readLines().drop(1)*.tokenize(',')*.first()
check('req05_groovy_product_ids_unique') { products*.id.unique(false).size() == products.size() }
check('req05_groovy_prices_positive_stock_valid') { products.every { it.price > 0 && it.stock >= 0 } }
check('req05_groovy_requirement_ids_unique') { reqIds.unique(false).size() == reqIds.size() }
System.exit(failed ? 1 : 0)
