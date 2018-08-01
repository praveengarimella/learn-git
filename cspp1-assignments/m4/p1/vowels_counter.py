#Assume s is a string of lower case characters.

#Write a program that counts up the number of vowels contained in the string s. Valid vowels are: 'a', 'e', 'i', 'o', and 'u'. For example, if s = 'azcbobobegghakl', your program should print:

#Number of vowels: 5

def main():
	s = raw_input()
	#your code here
	cnt = 0
	for c in s:
		if c in "aeiou":
			cnt += 1
	print (cnt)

if __name__== "__main__":
	main()
