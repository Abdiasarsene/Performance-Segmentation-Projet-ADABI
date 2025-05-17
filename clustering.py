# Importation librairies
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

# ====== IMPORTATION DU JEU DE DONNEES ======
client = pd.read_csv(r"../data/NewDataClient.csv")
print("Jeu de données importé ✅✅")

# ====== PRETRAITEMENT ======
# Séparation des colonnes dates
colonne_de_date_a_separer = ["date_inscription","date_dernier_achat"]
client =client.drop(columns=colonne_de_date_a_separer)

# Copie du jeu de données
data_client = client.copy()

# Séparation des types de données
num_col =data_client.select_dtypes(include=["int64","float64"]).columns.tolist()
cat_col = data_client.select_dtypes(include=['object']).columns.tolist()

# Définition de pipeline
num_transformer = Pipeline([
    ('impute', KNNImputer(n_neighbors=3)),
    ('scaler', StandardScaler())
])

cat_transformer = Pipeline([
    ("impute", SimpleImputer(strategy='constant',fill_value="Missing")),
    ("encoder", OneHotEncoder(sparse_output=False, handle_unknown='ignore'))
])

# Colum Transformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num',num_transformer,num_col),
        ('cat',cat_transformer,cat_col)
    ]
)

pipeline = Pipeline([
    ('preprocessing', preprocessor),
    ('pca',PCA(n_components=10))
])

# Application
data_transformed = pipeline.fit_transform(data_client)
print("ACP éffectué ✅✅")


# ====== CHOIX DU k-OPTIMAL POUR LE CLUSTERING ======
# Méthode de Elbow
inertias = []
for k in range(1,11):
    kmeans = KMeans(n_clusters= k, random_state=42)
    kmeans.fit_predict(data_transformed)
    inertias.append(kmeans.inertia_)

plt.plot(range(1,11), inertias, marker="o",linestyle='--')
plt.title("Methode de Elbow")
plt.xlabel("Nombre de Clusters")
plt.ylabel("Inerties")

# Silhouette Coefficient
silhouette_scores = []
for k in range(2,11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(data_transformed)
    score = silhouette_score(data_transformed, labels)
    silhouette_scores.append(score)

plt.figure(figsize=(8,5))
plt.plot(range(2,11), silhouette_scores, marker="o",linestyle="--")
plt.title("Methode de Silhouette Coefficient")
plt.xlabel("Nombre de clusters")
plt.ylabel("Silhouette score")
plt.show()

# ====== APPLICATION DU KMEANS ======
optimal_k =3
kmean = KMeans(n_clusters=3, random_state=42)
clusters = kmean.fit_predict(data_transformed)
data_transformed["Clusters"] = clusters
print("KMeans éffectué ✅✅")

# Centroids
pca = PCA(n_components=10)
data_pca = pca.fit_transform(data_transformed)
centroids = pca.transform(kmean.cluster_centers_)
print("ACP appliquée pour visualiser les centroids")

plt.figure(figsize=(8,6))
colors = ["black","orange","green"]

for i in range(optimal_k):
    plt.scatter(
        data_pca[clusters == i, 0],
        data_pca[clusters == i, 1],
        label =f"Clusters {i}",
        aplha =0.6,
        colors =colors[i]
    )

plt.scatter(centroids[:,0], centroids[:,1], marker="X", s=200,c="cyan", label ="Centroids")
plt.xlabel("ACP Composante 1")
plt.ylabel("ACP Composante 2")
plt.title(f"Visualisation KMeans Clusters(k={optimal_k})")
plt.legend()
plt.show()

# ====== ANALYSE DES MOYENNES ======
clusters_summary = data_client.groupby("Clusters")[num_col].mean()

# ====== CATEGORIES FREQUENTES PAR CLUSTER ======
for col in cat_col: 
    model_par_cluster = data_client.groupby("Clusters")[cat_col].agg(lambda x: x.mode()[0])
    print(f"\n Categorie la plus fréquente {col} selon chaque cluster\n {model_par_cluster}")

# ====== PROPORTION DE CLUSTER PAR CATEGORIES ======
# Categorie : Pays
cluster_proportion_pays = data_client.groupby("Clusters")["pays"].value_counts(normalize=True)

# Categorie : Statut des clients
cluster_proportion_statut_client = data_client.groupby("Clusters")["statut_client"].value_counts(normalize=True)