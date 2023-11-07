#include <stdio.h>
#include <stdlib.h>
#include <time.h>
     
char generateRandomChar() {


    // Define the character sets
    const char letters[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const char numbers[] = "0123456789";
    const char specialChars[] = "!@#$%^&*()_+-=[]{}|;:'\",.<>/?";

    int choice = rand() % 3;  // 0 for letters, 1 for numbers, 2 for special characters

    if (choice == 0) {
        return letters[rand() % 52];
    } else if (choice == 1) {
        return numbers[rand() % 10];
    } else {
        return specialChars[rand() % 29];
    }
}

void generatePassword(int numLetters, int numNumbers, int numSpecialChars) {

    printf("Generated Password: ");
    for (int i = 0; i < numLetters; i++) {
        printf("%c", generateRandomChar());
    }
    for (int i = 0; i < numNumbers; i++) {
        printf("%c", generateRandomChar());
    }
    for (int i = 0; i < numSpecialChars; i++) {
        printf("%c", generateRandomChar());
    }
    printf("\n");
}

int main() {
    srand(time(0)); // Seed the random number generator with the current time
    clock_t start_time = clock();
    int numLetters, numNumbers, numSpecialChars;

    printf("Enter the number of letters in the password: ");
    scanf("%d", &numLetters);
    printf("Enter the number of numbers in the password: ");
    scanf("%d", &numNumbers);
    printf("Enter the number of special characters in the password: ");
    scanf("%d", &numSpecialChars);

   
    generatePassword(numLetters, numNumbers, numSpecialChars);
    clock_t end_time = clock();

    double elapsed_time = (double)(end_time - start_time) / CLOCKS_PER_SEC;
    printf("Elapsed Time: %.5f seconds\n", elapsed_time);

    return 0;
}
