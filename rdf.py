from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF


DATABASE = "users.xml"
WORDS_DB = "words.xml"
EWEB_ONT = Namespace("project_ontology.owl#")
STD_WEIGHT = 1.0


def loadGraph(xml_file = DATABASE):
	graph = Graph()
	try:
		graph.parse(open(xml_file), format="xml")
	except:
		graph.bind("dc", DC)
		graph.bind("foaf", FOAF)
		graph.bind("eweb", EWEB_ONT)
	return graph

def addPerson(person, inter, graph = None):
	g = graph or loadGraph()

	# Create an identifier to use as the subject
	user = BNode()
	# Add triples using store's add method.
	g.add( (user, RDF.type, FOAF.Person) )
	g.add( (user, FOAF.name, Literal(person["name"])) )
	g.add( (user, FOAF.surname, Literal(person["surname"])) )
	g.add( (user, FOAF.gender, Literal(person["gender"])) )
	g.add( (user, FOAF.age, Literal(person["age"])) )
	g.add( (user, FOAF.based_near, Literal(person["country"])) )
	g.add( (user, FOAF.mbox, URIRef(person["email"])) )
	g.add( (user, FOAF.topic_interest, getInterestByDict(inter, g)) )

	save(g)

def getInterestByEmail(email, graph = None):
	g = graph or loadGraph()
	interest = {"where" : {"continents" : [], "countries" : []},
				"how" : {"areas" : [], "issues" : []},
				"who" : {"targets" : [], "subtypes" : []}}

	try: user = g.subjects(FOAF.mbox, URIRef(email)).__next__()
	except: return None

	inter = g.value(user, FOAF.topic_interest)

	# Get where: countries and continents
	loc = g.value(inter, EWEB_ONT.where)
	places = g.objects(loc, FOAF.based_near)
	for place in places:
		if(g.value(place, RDF.type) == EWEB_ONT.Country):
			for country in g.objects(place, FOAF.based_near):
				interest["where"]["countries"].append(str(country))
		elif(g.value(place, RDF.type) == EWEB_ONT.Continent):
			for continent in g.objects(place, FOAF.based_near):
				interest["where"]["continents"].append(str(continent))

	# Get who: targets and subtypes
	obj = g.value(inter, EWEB_ONT.who)
	target = g.value(obj, EWEB_ONT.who_target)
	for rep in g.objects(target, EWEB_ONT.represented_by):
		interest["who"]["targets"].append(str(rep))
	subtype = g.value(obj, EWEB_ONT.who_subtype)
	for rep in g.objects(subtype, EWEB_ONT.represented_by):
		interest["who"]["subtypes"].append(str(rep))

	# Get how: areas and issues
	tool = g.value(inter, EWEB_ONT.how)
	area = g.value(tool, EWEB_ONT.how_area)
	for domain in g.objects(area, EWEB_ONT.with_domain):
		interest["how"]["areas"].append(str(domain))
	issue = g.value(tool, EWEB_ONT.how_issue)
	for domain in g.objects(issue, EWEB_ONT.with_domain):
		interest["how"]["issues"].append(str(domain))

	return interest

def getWords(interest, graph = None):
	g = graph or loadGraph(WORDS_DB)
	wordsList = list()

	selected = interest["where"]["continents"]
	for c in g.subjects(RDF.type, EWEB_ONT.Continent):
		for continent in selected:
			if str(g.value(c, FOAF.name)) == continent:
				wordsList.append((continent, 2*STD_WEIGHT/len(selected)))
				[wordsList.append((str(w), STD_WEIGHT/len(selected)))
					for w in g.objects(c, DC.Subject)]

	selected = interest["where"]["countries"]
	for c in g.subjects(RDF.type, EWEB_ONT.Country):
		for country in selected:
			if str(g.value(c, FOAF.name)) == country:
				wordsList.append((country, 4*STD_WEIGHT/len(selected)))
				[wordsList.append((str(w), 2*STD_WEIGHT/len(selected)))
					for w in g.objects(c, DC.Subject)]

	selected = interest["how"]["areas"]
	for a in g.subjects(RDF.type, EWEB_ONT.Area):
		for area in selected:
			if str(g.value(a, FOAF.name)) == area:
				wordsList.append((area, 2*STD_WEIGHT/len(selected)))
				[wordsList.append((str(w), STD_WEIGHT/len(selected)))
					for w in g.objects(a, DC.Subject)]

	selected = interest["how"]["issues"]
	for i in g.subjects(RDF.type, EWEB_ONT.Issue):
		for issue in selected:
			if str(g.value(i, FOAF.name)) == issue:
				wordsList.append((issue, 4*STD_WEIGHT/len(selected)))
				[wordsList.append((str(w), 2*STD_WEIGHT/len(selected)))
					for w in g.objects(i, DC.Subject)]

	selected = interest["who"]["targets"]
	for t in g.subjects(RDF.type, EWEB_ONT.Target):
		for target in selected:
			if str(g.value(t, FOAF.name)) == target:
				wordsList.append((target, 2*STD_WEIGHT/len(selected)))
				[wordsList.append((str(w), STD_WEIGHT/len(selected)))
					for w in g.objects(t, DC.Subject)]

	selected = interest["who"]["subtypes"]
	for s in g.subjects(RDF.type, EWEB_ONT.Subtype):
		for subtype in selected:
			if str(g.value(s, FOAF.name)) == subtype:
				wordsList.append((subtype, 4*STD_WEIGHT/len(selected)))
				[wordsList.append((str(w), 2*STD_WEIGHT/len(selected)))
					for w in g.objects(s, DC.Subject)]

	return wordsList

def getInterestByDict(interest, g):
	"Returns a BNode() of type eweb:Interest with the required info"
	inter, loc, tool, obj = BNode(), BNode(), BNode(), BNode()
	cont, country, area = BNode(), BNode(), BNode()
	issue, target, subtype = BNode(), BNode(), BNode()

	g.add( (inter, RDF.type, EWEB_ONT.Interest) )
	g.add( (inter, EWEB_ONT.where, loc) )
	g.add( (inter, EWEB_ONT.how, tool) )
	g.add( (inter, EWEB_ONT.who, obj) )

	g.add( (loc, RDF.type, EWEB_ONT.Location) )
	g.add( (loc, FOAF.based_near, cont) )
	g.add( (loc, FOAF.based_near, country) )

	g.add( (tool, RDF.type, EWEB_ONT.Tool) )
	g.add( (tool, EWEB_ONT.how_area, area) )
	g.add( (tool, EWEB_ONT.how_issue, issue) )

	g.add( (obj, RDF.type, EWEB_ONT.Objective) )
	g.add( (obj, EWEB_ONT.who_target, target) )
	g.add( (obj, EWEB_ONT.who_subtype, subtype) )

	g.add( (cont, RDF.type, EWEB_ONT.Continent) )
	for c in interest["where"]["continents"]:
		g.add( (cont, FOAF.based_near, Literal(c)) )

	g.add( (country, RDF.type, EWEB_ONT.Country) )
	for c in interest["where"]["countries"]:
		g.add( (country, FOAF.based_near, Literal(c)) )

	g.add( (area, RDF.type, EWEB_ONT.Area) )
	for a in interest["how"]["areas"]:
		g.add( (area, EWEB_ONT.with_domain, Literal(a)) )

	g.add( (issue, RDF.type, EWEB_ONT.Issue) )
	for i in interest["how"]["issues"]:
		g.add( (issue, EWEB_ONT.with_domain, Literal(i)) )

	g.add( (target, RDF.type, EWEB_ONT.Target) )
	for t in interest["who"]["targets"]:
		g.add( (target, EWEB_ONT.represented_by, Literal(t)) )

	g.add( (subtype, RDF.type, EWEB_ONT.Subtype) )
	for s in interest["who"]["subtypes"]:
		g.add( (subtype, EWEB_ONT.represented_by, Literal(s)) )

	return inter

def save(graph, outfile=DATABASE, form="pretty-xml"):
	graph.serialize(destination=outfile, format=form)
