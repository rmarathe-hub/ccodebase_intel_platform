package com.example.users;

import com.example.users.api.UserApi;
import org.springframework.stereotype.Service;

@Service
public class UserService implements UserApi {
  public String find(String id) {
    return id;
  }
}
