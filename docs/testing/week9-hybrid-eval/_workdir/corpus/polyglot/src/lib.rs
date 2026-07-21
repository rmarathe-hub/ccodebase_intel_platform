pub fn greet(name: &str) -> String {
    format!("hello {}", name)
}

pub struct Point {
    pub x: i32,
    pub y: i32,
}

impl Point {
    pub fn origin() -> Self {
        Self { x: 0, y: 0 }
    }
}
