#include <iostream>
#include <algorithm>
#include <iomanip>
#include <vector>
#include <fstream>
#include <iomanip>
#include <ctime>
#include <cstdlib>
#include <climits>
#include <cstdio>
#include <random>
#include <cmath>
#include <cfloat>

void copy(double* a, double *b,  int size);

void copy(int* a, int *b,  int size);

void copy(double** a, double** b,  int size_x,  int size_y);

double distace(double* a, double* b,  int size);

void initialize(double** const samples, double** centers,  int n_samples,  int n_clusters,  int dimension);

double assign(double** const samples, double**  centers, int* labels,  int n_samples,  int n_clusters,  int dimension);

// returns true if was update, false when nothing changed
bool update(double** const samples, double** centers, int* cardinality, int* labels,  int n_samples,  int n_clusters,  int dimension,  double tolerance);

extern "C" void kmeans(double** const samples, double** _centers, int* _labels, double stats[4], int const n_samples,  int const n_clusters,  int const dimension,  double const tolerance,  int const n_init,  int const max_iter);