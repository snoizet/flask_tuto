from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#On crée un objet app qui représente notre application
app = Flask(__name__)

#On donne à notre application app l'emplacement de la base de données qu'elle devra
#utiliser. Les trois / indique un chemin relatif à l'emplacement de app.py sur le
#système. Cela évite d'avoir à écrire le chemin intégral vers la bdd.

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////~/Documents/flask/tuto/flask_full_tuto/test.db"


#On initialise notre base de données
db = SQLAlchemy(app)

#ATTENTION : penser à créer la db dans un shell python interactif: on tape python3
#dans le terminal (veiller à avoir activer son environnement virtuel) puis on
#from app import db (on remplace app par le nom de l'application en question ici
#il s'agit de app.py donc on tape app).
#db.create_all()


#On crée une classe càd un objet qui représente un ensemble d'attributs. On crée ici
#la classe Todo.
class Todo(db.Model):
	#On crée ensuite les attributs de cette classe.

	#Le premier attribut est id. On le définit comme un nombre entier. On 
	#utilisera cet attribut comme clé primaire càd que deux éléments de notre
	#base de donnée (de notre bdd ou de notre classe?) ne pourront pas avoir le
	#même id. Une clé primaire permet d'identifier uniquement les élements d'une
	#bdd.
	id = db.Column(db.Integer, primary_key=True)

	#On crée un second attribut que l'on appelle content et qui correspondra
	#dans le cadre de cette application aux tâches qu'il est possible de 
	#réaliser. On définit cet attribut comme une chaîne de moins de 200 
	#caractères. "nullable=False" indique que cet attribut ne pourra pas être
	#laissé vide dans le cadre de l'utilisation de l'application.
	content = db.Column(db.String(200), nullable=False)

	#On crée un troisième attribut que l'on nomme date_created et qui contiendra
	#la date de création de la tâche par l'utilisateur de l'application. Cet 
	#attribut est de type datetime. Le paramètre "default=datetime.utcnow"
	#permet de renvoyer comme attribut la date du jour lors de l'utilisation
	#de l'application pour crée une nouvelle tâche.
	date_created = db.Column(db.DateTime, default=datetime.utcnow)


	#On crée une fonction qui renvoie "Task" et le numéro id de la tâche à
	#chaque fois qu'une nouvelle tâche est créée.
	def __repr__(self):
		return '<Task %r>' % self.id


#On crée une route pour notre index (= notre sommaire), càd la page
#sur laquelle on doit arriver lorsque l'on tapera l'url de notre
#site. Cette route que l'on définit permet d'éviter une erreur 404
#lorsque l'on entrera l'url de notre site dans un navigateur.

#Dans cette route on ajoute l'option "methods" qui nous permet de définir les 
#actions réalisables par un utilisateur à partir de cette route. Ici on définit
#qu'il est possible pour un utilisateur d'envoyer des données vers la bdd de
#notre site à travers cet url ('POST') et de récupérer des données à partir de 
#notre bdd à partir de cette page ('GET').
@app.route('/', methods=['POST', 'GET'])
#On définit ensuite la fonction appelée lorsque l'on utilise cette
#route (càd lorsque l'on tape l'url de notre site dans un 
#navigateur.
def index():
	#Si la requête que l'on envoie à la route '/' qui correspond à l'url de index.html est POST
	#càd si l'on soumet un formulaire en cliquant sur "Add Task":
	if request.method == "POST":
	#alors on envoie ce que contient la requête POST, càd ce que contient le champ content du formulaire défini dans 
	#index.html, à notre base de données. Ce que contient le champ content est ici stocké dans une variable que l'on
	#créée et que l'on appelle task_content. request.form['content'] permet de sélectionner ce qui a été stocké dans le
	# champ "content" de l'objet form défini dans index.html.
		task_content = request.form['content']
		
		#On crée ensuite un objet new_task qui appartiendra à la classe Todo que nous avons précédemment créée
		#(càd que cet objet aura les attributs d'un objet de cette classe (à savoir: id, content, date_created)
		#et qu'il pourra ainsi intégrer notre base de données au sein de cette classe.
		new_task = Todo(content=task_content)
		
		#on pousse ensuite l'objet new_task dans notre bdd
		try:
			db.session.add(new_task)
			db.session.commit()
			#une fois l'objet poussé dans notre bdd on redirige l'utilisateur vers index.html
			return redirect('/')
		except:
			return "There was an issue adding your task."


	#sinon (càd dans le cas d'une requête GET) on affiche la page index.html
	else:
		#On crée un objet task qui va stocker toutes les tâches de la classe Todo et les classer par date de création.
		#A la place de .all() on aurait pu écrire .first() pour ne collecter que la première tâche créée.
		
		tasks = Todo.query.order_by(Todo.date_created).all()
		#tasks = Todo.query.all()
		
		#la fonction index() renvoie ici le template index.html grâce à la 
		#fonction render_template(). tasks=tasks renvoie le template index.html en y intégrant toutes les tâches stockées
		#dans tasks.
		return render_template('index.html', tasks=tasks)
		#return render_template('index.html')

#on crée une route qui renvoie vers l'url de la page à afficher lorsqu'un utilisateur cliquera sur delete. Dans cette route <int:id> correspond à 
#l'id de la tâche que l'on souhaite supprimer.
@app.route('/delete/<int:id>')
#On définit ensuite la fonction appelée lorsque l'on utilise cette
#route (càd lorsqu'un utilisateur clique sur delete). Cette fonction 
#s'applique à la variable id qui un entier unique qui représente une
#tâche.
def delete(id):
	#on crée une varibale task_to_delete qui va contenir l'id de la tâche que l'on souhaite supprimer. Si cet id n'existe pas dans
	#notre db la fonction nous renverra une erreur 404.
	task_to_delete = Todo.query.get_or_404(id)

	try:
		#dans notre db on supprime la ligne qui correspond à la tâche dont l'id est celui stocké dans la variable task_to_delete
		db.session.delete(task_to_delete)
		#ne pas oublié de transmettre cette action à notre db en utilisant commit
		db.session.commit()
		#puis une fois la suppression effectuée on renvoie l'utilisateur sur la page d'acceuil index.html
		return redirect('/')
	except:
		return "There was a problem deleting that task."


#on fait la même chose pour update sauf que la route comprend le paramètre methods dans la mesure où lorsque l'utilisateur
#cliquera sur update, il modifiera la db et devra donc modifier la db via la méthode POST.
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	#on crée une variable task qui récupère la tâche dans notre db à partir de son l'id de la tâche que l'on souhaite
	#mettre à jour.
	task = Todo.query.get_or_404(id)

	if request.method == 'POST':
		#si l'utilisateur utilise la méthode POST càd s'il souhaite modifier le contenu d'une tâche alors
		#on assigne au contenu de la variable task (que l'on vient de reconstituer à partir de notre db et de
		#l'id de la tâche en question) le contenu de ce que l'utilisateur rentre dans le champ content du 
		#formulaire du template update.html.
		task.content = request.form['content']
		#On essaye ensuite d'ajouter cette mise à jour de la tâche à notre db
		try:
			db.session.commit()
			#puis on redirige l'utilisateur sur la page d'accueil index.html via la route '/'
			return redirect('/')
		except:
			return "There was an issue updating your task."
	else:
		#on renvoie le template update.html lorsque l'utilisateur fait un GET sur cette route /update/ càd lorsqu'il
		#clique sur update à côté d'une tâche sur l'interface graphique. On définit que la variable task de update.html
		#est égale à la variable task de la fonction update(). Ainsi le template update.html s'adaptera à chaque tâche.
		return render_template('update.html', task=task)


if __name__ == "__main__":
	app.run(debug=True) 
