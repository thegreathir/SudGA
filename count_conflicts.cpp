#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

unsigned int count_conflicts(const std::vector<std::vector<int>> &sudoku)
{
    unsigned short counter[3][9][9] = {};

    for (unsigned short i = 0; i < 9; ++i)
        for (unsigned short j = 0; j < 9; ++j)
        {
            unsigned int cell = sudoku[i][j] - 1;
            counter[0][i][cell]++;
            counter[1][j][cell]++;
            counter[2][((i / 3) * 3) + (j / 3)][cell]++;
        }

    unsigned int result = 0;

    for (unsigned short k = 0; k < 3; ++k)
        for (unsigned short i = 0; i < 9; ++i)
            for (unsigned short j = 0; j < 9; ++j)
            {
                unsigned short c = counter[k][i][j];
                if (c > 1)
                    result += (c * (c - 1));
            }
    
    return result;
}

PYBIND11_MODULE(count_conflicts_cpp, m)
{
    m.def("count_conflicts", &count_conflicts);
}