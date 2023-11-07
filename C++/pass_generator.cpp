#include <iostream>
#include <ctime>
#include <cstdlib>
#include <algorithm>

using namespace std;
 clock_t start_time = clock();
string generatePassword(int numLetters, int numNumbers, int numSpecialChars) {
    string allChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    string numbers = "0123456789";
    string specialChars = "!@#$%^&*()_+-=[]{}|;:'\",.<>/?";

    string password;
    
    for (int i = 0; i < numLetters; i++) {
        password += allChars[rand() % allChars.length()];
    }
    for (int i = 0; i < numNumbers; i++) {
        password += numbers[rand() % numbers.length()];
    }
    for (int i = 0; i < numSpecialChars; i++) {
        password += specialChars[rand() % specialChars.length()];
    }

    random_shuffle(password.begin(), password.end());

    return password;
}

int main() {
    int numLetters, numNumbers, numSpecialChars;
    
    cout << "Enter the number of letters in the password: ";
    cin >> numLetters;
    cout << "Enter the number of numbers in the password: ";
    cin >> numNumbers;
    cout << "Enter the number of special characters in the password: ";
    cin >> numSpecialChars;

    srand(time(0));  // Seed the random number generator with the current time

   
    string password = generatePassword(numLetters, numNumbers, numSpecialChars);
    clock_t end_time = clock();
    
    cout << "Generated Password: " << password << endl;
    cout << "Elapsed Time: " << static_cast<double>(end_time - start_time) / CLOCKS_PER_SEC << " seconds" << endl;

    return 0;
}
