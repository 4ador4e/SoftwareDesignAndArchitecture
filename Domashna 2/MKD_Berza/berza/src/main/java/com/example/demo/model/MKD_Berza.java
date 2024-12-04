package com.example.demo.model;
import jakarta.persistence.*;
import jakarta.persistence.Entity;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.sql.Date;


@Data
@Entity
@Table(name = "MKD_Berza")
@NoArgsConstructor
@AllArgsConstructor
public class MKD_Berza implements Serializable {

    /**
     *
     */
    private static final long serialVersionUID = 898002081458478671L;
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long Sifra;
    @NotNull(message = "Sifrata mora da postoi")
    @Column(unique = true)
    @Positive(message = "Cenata na poslednata transakcija mora da e pogolema od 0")
    private Integer cena_trans;
    @Positive(message = "Prometot mora da e pogolem od 0")
    private Integer promet;
    private Date data;
}
