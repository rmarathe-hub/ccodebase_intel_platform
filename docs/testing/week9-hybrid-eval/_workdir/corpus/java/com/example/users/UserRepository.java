package com.example.users;

import org.springframework.stereotype.Repository;

@Repository
public class UserRepository {
  public String findById(String id) {
    return id;
  }
}
