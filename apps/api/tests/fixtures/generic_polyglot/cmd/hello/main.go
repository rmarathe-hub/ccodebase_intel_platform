package main

func Hello(name string) string {
	return "hello " + name
}

type User struct {
	Name string
}

func main() {
	_ = Hello("world")
}
