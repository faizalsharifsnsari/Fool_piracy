#include <iostream>
#include <fstream>
#include <cctype>

using namespace std;

int main() {
    ifstream file("sample.txt");

    if (!file) {
        cout << "Error: Cannot open file." << endl;
        return 1;
    }

    char ch;
    int letters = 0;
    int vowels = 0;
    int lines = 0;

    while (file.get(ch)) {
        
        // Count lines
        if (ch == '\n') {
            lines++;
        }

        // Count letters
        if (isalpha(ch)) {
            letters++;

            char lower = tolower(ch);

            if (lower == 'a' || lower == 'e' || lower == 'i' || 
                lower == 'o' || lower == 'u') {
                vowels++;
            }
        }
    }

    // If file doesn't end with newline
    if (letters > 0)
        lines++;

    double avgLetters = 0;
    if (lines > 0)
        avgLetters = (double)letters / lines;

    cout << "Number of letters: " << letters << endl;
    cout << "Number of lines: " << lines << endl;
    cout << "Average letters per line: " << avgLetters << endl;
    cout << "Number of vowels: " << vowels << endl;

    file.close();
    return 0;
}
