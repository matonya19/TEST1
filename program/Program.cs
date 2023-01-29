// Написать программу, которая из имеющегося массива строк формирует массив из строк, длина которых равна
// либо меньше 3 символов.

	string[] arr1 = {"Hello", "2", "world", ":-)"};
	string[] arr2 = {"1234", "1567", "-2", "computer science"};
	string[] arr3 = {"Russia", "Denmark", "Kazan"};
		
	string[] GetShortWordsArray(string[] array)
        {
            int wordLength = array.Length;          
            string[] result = new string[wordLength];
            int count = 0;
            
            for (int i = 0; i < wordLength; i++)
            {
                if(array[i].Length <= 3)
                {
                    result[count] = array[i];
                    count++;
                }
            }
            Array.Resize(ref result, count);
            
            return result;
        }
        
