#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

inline unsigned int count_conflicts(const std::vector<std::vector<int>> &sudoku) noexcept
{
    unsigned short counter[3][9][9] = {};

    unsigned int result = 0;

    for (unsigned short i = 0; i < 9; ++i)
        for (unsigned short j = 0; j < 9; ++j)
        {
            unsigned int cell = sudoku[i][j] - 1;
            result += counter[0][i][cell]++;
            result += counter[1][j][cell]++;
            result += counter[2][((i / 3) * 3) + (j / 3)][cell]++;
        }

    return result;
}

PYBIND11_MODULE(count_conflicts_cpp, m)
{
    m.def("count_conflicts", &count_conflicts);
}
