package com.example.demo.user;

import org.springframework.stereotype.Repository;

@Repository
public class UserRepository {
  public UserEntity findById(Long id) {
    UserEntity entity = new UserEntity();
    entity.setId(id);
    entity.setName("user-" + id);
    return entity;
  }
}
