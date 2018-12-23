#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE Test

// Aby skompilować testy należy użyć polecenia 
// g++ -std=c++11 -o test unit_tests.cpp my_kmeans.cpp -lboost_unit_test_framework

#include <boost/test/unit_test.hpp>
#include <float.h>
#include "my_kmeans.h"
#include "ctime"
#include "cstdlib"

BOOST_AUTO_TEST_SUITE( KMeans )

BOOST_AUTO_TEST_CASE( copy_test )
{
        int size = 10;

        double* a = new double[size];
        double* b = new double[size];

        for(int i = 0; i < size; i++)
        {
                a[i] = i;
        }

        copy(b,a,size);

        for(int i = 0; i < size; i++)
        {
                BOOST_CHECK_EQUAL(a[i], b[i]);
        }

}

BOOST_AUTO_TEST_CASE( distance_euclidean )
{
        int size = 2;

        double* a = new double[size];
        double* b = new double[size];
        double* c = new double[size];

        a[0] = 1;
        a[1] = 2;
        b[0] = 4;
        b[1] = 6;
        c[0] = 2002;
        c[1] = 646;

        BOOST_CHECK_EQUAL(distace(a,b,size), distace(b,a,size));
        BOOST_CHECK_EQUAL(distace(a,b,size), 5);
	BOOST_CHECK_EQUAL(distace(c,b,size), 2098);
	BOOST_CHECK_EQUAL(distace(c,c,size), 0);
}


BOOST_AUTO_TEST_CASE( initialize_test )
{
	srand(time(NULL));

	int n_samples = 1000;
	int n_clusters = 6;
	int dimension = 10;

	double** samples = new double*[n_samples];
	for(int i = 0; i < n_samples; i++)
	{
		samples[i] = new double[dimension];
		for(int j = 0; j < dimension; j++)
		{
			samples[i][j] = std::rand()%RAND_MAX;
		}
	}
	double** centers  = new double*[n_clusters];
	for(int i = 0; i < n_clusters; i++)
	{
		centers[i] = new double[dimension];
	}

	initialize(const_cast<const double**>(samples), centers, n_samples, n_clusters, dimension);

	int count = 0;
	for(int i = 0; i < n_clusters; i++)
	{
		for(int j = 0; j < n_samples; j++)
		{
			bool flag = true;
			for(int d = 0; d < dimension; d++)
			{
				if(samples[i][j] != centers[i][j])
				{
					flag = false;
					break;
				}
			}
			if(flag)
			{
				count++;
				break;
			}
		}
	}	

	BOOST_REQUIRE(count >= 6);	
}

BOOST_AUTO_TEST_CASE( assign_test )
{
	srand(time(NULL));

	int n_samples = 1000;
	int n_clusters = 6;
	int dimension = 10;

	int* labels = new int[n_samples];

	double** samples = new double*[n_samples];
	for(int i = 0; i < n_samples; i++)
	{
		samples[i] = new double[dimension];
		for(int j = 0; j < dimension; j++)
		{
			samples[i][j] = std::rand()%RAND_MAX;
		}
	}
	double** centers  = new double*[n_clusters];
	for(int i = 0; i < n_clusters; i++)
	{
		centers[i] = new double[dimension];
	}

	initialize(const_cast<const double**>(samples), centers, n_samples, n_clusters, dimension);

	assign(const_cast<const double**>(samples), centers, labels, n_samples, n_clusters, dimension);

	for(int j = 0; j < n_samples; j++)
	{
		BOOST_REQUIRE(labels[j] < n_clusters);
		BOOST_REQUIRE(labels[j] >= 0);
	}
}


BOOST_AUTO_TEST_SUITE_END()
