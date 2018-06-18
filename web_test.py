#!/usr/bin/env python

import cherrypy
import json
import rdf
import codecs
import searcher

INTERESTS = {"continents" : {"south america": ["venezuela", "brazil", "colombia"],
							"africa": ["kenya", "tanzania", "cameroon"],
							"europe": ["turkey", "bulgaria", "ukraine"]},
			"areas" : {"science": ["medicine", "psychology", "economics"],
					   "culture": ["languages", "sexuality", "events"],
					   "society": ["bullying", "racism", "war"]},
			"targets" : {"people": ["young", "old", "poor", "sick"],
						 "animals": ["abandoned", "extinction risk"],
						 "places": ["natural", "historical", "cultural"]}}


class UsersTest(object):
	interest = {"where" : {"continents" : [], "countries" : []},
        "how" : {"areas" : [], "issues" : []},
        "who" : {"targets" : [], "subtypes" : []}}
	user, words = None, None

	@cherrypy.expose
	def index(self):
		return """<html>
			<head></head>
			<body>
			<h1>User test</h1>

			<h2>Upload a JSON file with your personal info</h2>
			<form method="post" enctype="multipart/form-data" action="startTest" onsubmit="return isValid('jsonFile')">
				<input type="file" accept=".json" name="jsonFile" id="jsonFile"/><br>
				<input type="submit" value="Start!">
			</form>

			<h2>Or enter your email to start a ONG recommendation</h2>
			<form method="post" action="startSearch" onsubmit="return validateEmail('email')">
				<input type="text" name="email" id="email"><br><br>
				<input type="submit" value="Start!">
			</form>			

			<script>
				function isValid(id) {
					return document.getElementById(id).value != "";
				}
			</script>

			<script>
				function validateEmail(email) {
 					var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    				return re.test(String(getElementById(email)).toLowerCase());
    			}
			</script>

			</body>
			</html>"""

	@cherrypy.expose
	def startTest(self, jsonFile = None):
		"Main menu to select interest"

		reader = codecs.getreader("utf-8")
		if jsonFile is not None: UsersTest.user = json.load(reader(jsonFile.file))
		out = """<html><body>
				<h2>Select different interests</h2>

				<form method=post action="selectWhere">
					<fieldset>
						<legend> Where would you like to help? </legend>
						{0}
						<br><br>
						<input type="submit" value="Select">
					</fieldset>
				</form>

				<form method=post action="selectHow">
					<fieldset>
						<legend> How would you like to help? </legend>
						{1}
						<br><br>
						<input type="submit" value="Select">
					</fieldset>
				</form>

				<form method=post action="selectWho">
					<fieldset>
						<legend> Who/What would you like to help? </legend>
						{2}
						<br><br>
						<input type="submit" value="Select">
					</fieldset>
				</form>

				<form method=post action="save">
					Save profile:<br>
					<br><button type="submit">Save!</button><br>
				</form>

				</body></html>"""

		continents = ['<input type="checkbox" name="continents" value="{0}">{0}'.format(c)
			for c in list(INTERESTS["continents"].keys())]

		areas = ['<input type="checkbox" name="areas" value="{0}">{0}'.format(a)
			for a in list(INTERESTS["areas"].keys())]

		targets = ['<input type="checkbox" name="targets" value="{0}">{0}'.format(t)
			for t in list(INTERESTS["targets"].keys())]

		return out.format("<br>".join(continents), "<br>".join(areas), "<br>".join(targets))

	@cherrypy.expose
	def selectWhere(self, continents = []):
		"Select countries"
		if isinstance(continents, str): continents = [continents]
		for conti in continents:
			UsersTest.interest["where"]["continents"].append(conti)

		out = """<html><body>
				<h2>Select different countries</h2>

				<form method=post action="saveWhere">
					<fieldset>
						<legend> Where would you like to help? </legend>
						{0}
						<br><br>
						<input type="submit" value="Save">
					</fieldset>
				</form>

				</body></html>"""

		countries = list()
		for continent in continents:
			for country in INTERESTS["continents"][continent]:
				countries.append('<input type="checkbox" name="countries" value="{0}">{0}'.format(country))

		return out.format("<br>".join(countries))

	@cherrypy.expose
	def saveWhere(self, countries = []):
		"Save countries"
		if isinstance(countries, str): countries = [countries]
		for country in countries:
			UsersTest.interest["where"]["countries"].append(country)

		raise cherrypy.HTTPRedirect('/startTest')

	@cherrypy.expose
	def selectHow(self, areas=[]):
		"Select issues"
		if isinstance(areas, str): areas = [areas]
		for are in areas:
			UsersTest.interest["how"]["areas"].append(are)

		out = """<html><body>
					<h2>Select different area</h2>

					<form method=post action="saveHow">
						<fieldset>
							<legend> How would you like to help? </legend>
							{0}
							<br><br>
							<input type="submit" value="Save">
						</fieldset>
					</form>

					</body></html>"""

		issues = list()
		for area in areas:
			for iss in INTERESTS["areas"][area]:
				issues.append('<input type="checkbox" name="issues" value="{0}">{0}'.format(iss))

		return out.format("<br>".join(issues))

	@cherrypy.expose
	def saveHow(self, issues=[]):
		"Save issues"
		if isinstance(issues, str): issues = [issues]
		for issue in issues:
			UsersTest.interest["how"]["issues"].append(issue)

		raise cherrypy.HTTPRedirect('/startTest')

	@cherrypy.expose
	def selectWho(self, targets=[]):
		"Select issues"
		if isinstance(targets, str): targets = [targets]
		for tar in targets:
			UsersTest.interest["who"]["targets"].append(tar)

		out = """<html><body>
						<h2>Select different targets</h2>

						<form method=post action="saveWho">
							<fieldset>
								<legend> Who would you like to help? </legend>
								{0}
								<br><br>
								<input type="submit" value="Save">
							</fieldset>
						</form>

						</body></html>"""

		subtypes = list()
		for target in targets:
			for subty in INTERESTS["targets"][target]:
				subtypes.append('<input type="checkbox" name="subtypes" value="{0}">{0}'.format(subty))

		return out.format("<br>".join(subtypes))

	@cherrypy.expose
	def saveWho(self, subtypes=[]):
		"Save issues"
		if isinstance(subtypes, str): subtypes = [subtypes]
		for subtype in subtypes:
			UsersTest.interest["who"]["subtypes"].append(subtype)

		raise cherrypy.HTTPRedirect('/startTest')

	@cherrypy.expose
	def save(self):
		rdf.addPerson(UsersTest.user, UsersTest.interest)
		raise cherrypy.HTTPRedirect('/index')

	@cherrypy.expose
	def startSearch(self, email):
		interest = rdf.getInterestByEmail(email)
		if interest is None:
			raise cherrypy.HTTPRedirect('/index')
		UsersTest.words = rdf.getWords(interest)

		return """<body><html>
				<h2>Set additional keywords:</h2>
				<form method=post action="search">
					<input type="text" name="keywords"><br><br>
					<input type="text" name="keywords"><br><br>
					<input type="text" name="keywords"><br><br>
					<input type="text" name="keywords"><br><br>
					<br><button type="submit">Search!</button><br>
				</form>

				</body></html>"""

	@cherrypy.expose
	def search(self, keywords):
		if isinstance(keywords, str): keywords = [keywords]
		[UsersTest.words.append((str(w), rdf.STD_WEIGHT*10)) for w in keywords if len(w) > 0]

		out = "<body><html>{0}</body></html>"
		ongs = [title + " -> " + str(rel) for title,rel in searcher.getResult(UsersTest.words)]
		return out.format("<br>".join(ongs))


if __name__ == '__main__':
	cherrypy.quickstart(UsersTest())
