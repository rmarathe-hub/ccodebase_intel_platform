package com.example.demo.user;

import org.springframework.stereotype.Service;

@Service
public class UserServiceImpl implements UserService {
  private final UserRepository repository;

  public UserServiceImpl(UserRepository repository) {
    this.repository = repository;
  }

  @Override
  public UserEntity findById(Long id) {
    return repository.findById(id);
  }
}
