/*

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

Plik źródłowy z implementacją algorytmu k-średnich. Komilowany do biblioteki dzielonej. 

Aby skompilować plik do biblioteki dzielonej (my_kmeans.so) należy użyć polecenia: 
g++ -std=c++11 -o my_kmeans.so -fPIC -shared my_kmeans.cpp -I/usr/include/python2.7


*/

#include "my_kmeans.h"

void copy(double* a, double *b,  int size)
{
    for(int i = 0; i < size; i++)
    {
        a[i] = b[i];
    }
}

void copy(int* a, int *b,  int size)
{
    for(int i = 0; i < size; i++)
    {
        a[i] = b[i];
    }
}

void copy(double** a, double** b,  int size_x,  int size_y)
{
    for(int i = 0; i < size_x; i++)
    {
        for(int j = 0; j < size_y; j++)
        {
            a[i][j] = b[i][j];
        }
    }
}

// funkcja obliczająca dystans pomiędzy n-wymiarowymi punktami
double distace(double* a, double* b,  int size)
{
    double distance = 0;
    for(int i = 0; i < size; i++)
    {
        distance += pow((a[i] - b[i]),2);
    }
    return sqrt(distance);
}

// funkcja inicjalizująca, wybiera początkowe środki (centroidy) zgodnie z metodą k-means++
void initialize(double** const samples, double** centers,  int n_samples,  int n_clusters,  int dimension)
{
    // ustawienie pierwszego centroidu losowo
    copy(centers[0],samples[rand()%n_samples], dimension);

    // ustawienie pozostałych centroidów oparciu o prawdopodobieństwo proporcjonalne do D(x)
    for(int i = 1; i < n_clusters; i++)
    {
        double largest_shortest_distance_to_center = 0;
        double shortest_distances_to_centers[n_samples];
        int index_of_the_point_with_largest_shortest_distance_to_center= -1;
        // dla każdego punktu wybieram centroid (już ustalony) leżący najbliżej niego
        for(int j = 0; j < n_samples; j++)
        {
            double nearest_center_distance = DBL_MAX;
            for(int k = 0; k < i; k++)
            {
                double center_distance = distace(centers[k],samples[j],dimension);
                if(center_distance < nearest_center_distance)
                {
                    nearest_center_distance = center_distance;
                }
            }
            shortest_distances_to_centers[j] = nearest_center_distance;
            if(nearest_center_distance > largest_shortest_distance_to_center)
            {
                largest_shortest_distance_to_center = nearest_center_distance;
                index_of_the_point_with_largest_shortest_distance_to_center = j;
            }
        }
	
	// realizuję losowy wybór kolejnego centroidu
        int tokens[n_samples];
        for(int t = 0; t < n_samples; t++)
        {
            tokens[t] = (int)(100*shortest_distances_to_centers[t]/largest_shortest_distance_to_center);
        }
        int lottery = rand()%(10*n_samples);
        int lucky = -1;
        for(int t = 0; t < n_samples; t++)
        {
            lottery -= tokens[t];
            if (lottery <= 0)
            {
                lucky = t;
                break;
            }
            if(t == n_samples -1)
            {
                t = -1;
            }
        }
        copy(centers[i],samples[lucky],dimension);
    }
}

// przypisanie wszytstkich punktów do środka (centroidu) leżącego najbliżej danego punktu
// funkcja oblicza i zwraca WCSS (within cluster sum of squares)
double assign(double** const samples, double**  centers, int* labels,  int n_samples,  int n_clusters,  int dimension)
{
    double wcss = 0;
    for(int i = 0; i < n_samples; i++)
    {
        double nearest_cluster_distance = DBL_MAX;
        int nearest_cluster_label = -1;
        for(int j = 0; j < n_clusters; j++)
        {
            double cluster_distance = distace(centers[j],samples[i],dimension);
            if(cluster_distance < nearest_cluster_distance)
            {
                nearest_cluster_distance = cluster_distance;
                nearest_cluster_label = j;
            }
        }
        labels[i] = nearest_cluster_label;
        wcss += pow(nearest_cluster_distance,2);
    }
    return wcss;
}

// funkcja aktualizuąca położenie centroidów, nowy cetroid jest średnią arytmetyczną punktów do niego przypisanych
// zwraca false jeśli położenie nowych centroidów nie uległo zmianie większej niż tolerancja
// UWAGA: jest to tolerancja inna niż 'względna tolerancja WCSS' przekazywana jako parametr algorytmu k-średnich
bool update(double** const samples, double** centers, int* cardinality, int* labels,  int n_samples,  int n_clusters,  int dimension,  double tolerance)
{
    double** new_centers;
    new_centers = new double*[n_clusters];
    for(int i = 0; i < n_clusters; i++)
    {
        new_centers[i] = new double[dimension];
    }
    int new_centers_cardinality[n_clusters];
    for(int i = 0; i < n_clusters; i++)
    {
        new_centers_cardinality[i] = 0;
        for(int j = 0; j < dimension; j++)
        {
            new_centers[i][j] = 0;
        }
    }
    for(int i = 0; i < n_samples; i++)
    {
        for(int j = 0; j < dimension; j++)
        {
            new_centers[labels[i]][j] += samples[i][j];
        }
        new_centers_cardinality[labels[i]] += 1;
    }
    for(int i = 0; i < n_clusters; i++)
    {
        cardinality[i] = new_centers_cardinality[i];
        for(int j = 0; j < dimension; j++)
        {
            new_centers[i][j] /= new_centers_cardinality[i];
        }
    }
    // sprawdzenie czy centroidy uległy wymaganej minimalnej zmianie
    for(int i = 0; i < n_clusters; i++)
    {
        if(distace(centers[i],new_centers[i],dimension) > tolerance)
        {
            copy(centers,new_centers,n_clusters,dimension);
            for(int i = 0; i < n_clusters; i++)
                delete [] new_centers[i];
            delete [] new_centers;
            return true;
        }
    }

    for(int i = 0; i < n_clusters; i++)
        delete [] new_centers[i];
    delete [] new_centers;

    return false;
}

// funkcja realizująca algorytm k-średnich
extern "C" void kmeans(double** const samples, double** _centers, int* _labels, double stats[4], int const n_samples,  int const n_clusters,  int const dimension,  double const tolerance,  int const n_init,  int const max_iter)
{
    srand(time(NULL));

    double BEST_wcss = DBL_MAX;

    int max_iter_run = 0;

    int all_iter_run = 0;

    int number_of_the_BEST_initialization_ = 0;

    // 'point_tolerance' to inna tolerancja niż 'tolerance'. Ta pierwsza dotyczy zmiany położenia centroidu, ta druga względnej zmiany WCSS.
    double point_tolerance = 0.0001;


    // główny algorytm
    for(int initialization = 1; initialization <= n_init; initialization++)
    {
        double** centers;
        centers = new double*[n_clusters];
        int cardinality[n_clusters];
        for(int i = 0; i < n_clusters; i++)
        {
            cardinality[i] = 0;
            centers[i] = new double[dimension];
        }
        int labels[n_samples];
        double wcss = 0;
        double old_wcss = DBL_MAX;

        initialize(samples,centers,n_samples,n_clusters,dimension);

        int iteration = 1;
        for(iteration = 1; iteration <= max_iter; ++iteration)
        {
            wcss = assign(samples,centers,labels,n_samples,n_clusters,dimension);
            if(update(samples,centers,cardinality,labels,n_samples,n_clusters,dimension,point_tolerance) && iteration != max_iter)
            {
                if(wcss/old_wcss > 1 - tolerance)
                {
                    break;
                }
                old_wcss = wcss;
                continue;
            }
            else
            {
                break;
            }
        }
        all_iter_run += iteration;
        if(iteration > max_iter_run)
        {
            max_iter_run = iteration;
        }
        if(wcss < BEST_wcss)
        {
            number_of_the_BEST_initialization_ = initialization;
            BEST_wcss = wcss;
            copy(_labels,labels,n_samples);
            copy(_centers,centers,n_clusters,dimension);
        }

        for(int i = 0; i < n_clusters; i++)
            delete [] centers[i];
        delete [] centers;
    }

    // ustawienie statystyk

    stats[0] = number_of_the_BEST_initialization_;

    stats[1] = all_iter_run;

    stats[2] = max_iter_run;

    stats[3] = BEST_wcss;
}
