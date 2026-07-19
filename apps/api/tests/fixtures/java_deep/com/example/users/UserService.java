package com.example.users;

import com.example.users.api.UserApi;
import org.springframework.stereotype.Service;

@Service
public class UserService implements UserApi {
  private final UserRepository repo;

  public UserService(UserRepository repo) {
    this.repo = repo;
  }

  public String find(String id) {
    helper();
    this.helper();
    return repo.findById(id);
  }

  private void helper() {}
}
